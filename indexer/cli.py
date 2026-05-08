# indexer/cli.py
from __future__ import annotations
import logging
import os
import subprocess
from fnmatch import fnmatch
from pathlib import Path

logger = logging.getLogger(__name__)

import click

from indexer.config import Config, load_config, save_config
from indexer.manifest import load_manifest, save_manifest
from indexer.git import (
    staged_files, all_tracked_files, current_commit, current_branch,
    changed_files_since, is_git_repo
)
from indexer.ast_parser import parse_file, load_cached_nodes, save_cached_nodes, compute_hash_short
from indexer.llm import describe_nodes, describe_files, deep_enrich_pages, deep_enrich_index, synthesize_commit_message
from indexer.grouper import density_group
from indexer.hooks import install_hook, remove_hook
from indexer.indexing import (
    cross_reference, load_existing_nodes, parse_candidates,
    build_batches, write_wiki_pages, write_index_and_skill,
    update_manifest, upsert_vectors,
)

CLAUDEMD_SNIPPET = """
## Codebase Navigation

This repo is indexed with repo-wiki. Before reading any source file or answering any code question:

1. Load `.indexer/skills/codebase.md` as a skill — it contains the full navigation workflow.
2. Read `wiki/INDEX.md` for the system overview and module map.
3. Match the question to a wiki page, look up symbols there, and only read source when you know the exact file and line range.

Do not read source files speculatively. The wiki gives you structure and relationships in a fraction of the tokens.

- Wiki pages: `wiki/` — grouped by logical density, not directory structure
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs
- Component IDs: `relative/path.py::ClassName.method_name`
"""


@click.group()
def main():
    pass


@main.command()
def init():
    """Create .indexer.toml, install pre-commit hook, append to CLAUDE.md."""
    root = Path.cwd()
    cfg = load_config(root)
    save_config(root, cfg)
    click.echo(f"Created {root / '.indexer.toml'}")

    _ensure_cache_gitignore(root, verbose=True)

    if is_git_repo(root) and cfg.pre_commit:
        install_hook(root, skip_deep=not cfg.deep_hook)
        mode = "--staged --skip-deep" if not cfg.deep_hook else "--staged"
        click.echo(f"Installed pre-commit hook  (repo-wiki run {mode})")

    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        existing = claude_md.read_text()
        if "Codebase Navigation" not in existing:
            claude_md.write_text(existing + "\n" + CLAUDEMD_SNIPPET)
            click.echo("Appended to CLAUDE.md.")
    else:
        claude_md.write_text(CLAUDEMD_SNIPPET.lstrip())
        click.echo("Created CLAUDE.md.")


@main.command()
@click.option("--staged", is_flag=True, help="Incremental: only staged files (used by hook)")
@click.option("--force", is_flag=True, help="Force full re-index regardless of manifest")
@click.option("--skip-deep", is_flag=True, help="Skip narrative, data flows, and design constraints (faster, fewer tokens)")
def run(staged: bool, force: bool, skip_deep: bool):
    """Index the codebase and generate wiki pages."""
    root = Path.cwd()
    cfg = load_config(root)
    manifest = load_manifest(root)

    _ensure_cache_gitignore(root)

    if is_git_repo(root):
        all_git_files = all_tracked_files(root)
    else:
        all_git_files = [
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)
        ]
    tracked_files = [f for f in all_git_files if _is_indexable(f, cfg)]

    if staged:
        candidates = staged_files(root)
    elif force or manifest.last_indexed_commit is None:
        candidates = tracked_files
    else:
        try:
            git_changed = changed_files_since(root, manifest.last_indexed_commit) if is_git_repo(root) else []
        except ValueError:
            logger.warning("Last indexed commit %s is no longer valid, falling back to full index", manifest.last_indexed_commit)
            git_changed = all_git_files
        stale = manifest.stale_files(root, tracked_files)
        candidates = list(dict.fromkeys(git_changed + stale))

    candidates = [f for f in candidates if _is_indexable(f, cfg)]

    if not candidates:
        click.echo("  Nothing to index.")
        return

    mode = "staged" if staged else ("full re-index" if force else "incremental")
    click.echo(f"\n  repo-wiki  —  {mode}  —  {len(candidates)} file(s)\n")

    # ── Phase 1: Parse ────────────────────────────────────────────────────────
    click.echo("  Parsing")
    all_nodes = []
    cached_count = 0
    for rel_path in candidates:
        abs_path = root / rel_path
        file_hash = compute_hash_short(abs_path)
        cached = load_cached_nodes(root, file_hash)
        if cached is not None:
            all_nodes.extend(cached)
            cached_count += 1
            click.echo(f"    ✓  {rel_path}  (cached)")
        else:
            nodes = parse_file(abs_path, root)
            save_cached_nodes(root, file_hash, nodes)
            all_nodes.extend(nodes)
            symbol_count = len(nodes)
            click.echo(f"    ✓  {rel_path}  ({symbol_count} symbol{'s' if symbol_count != 1 else ''})")

    if not all_nodes:
        click.echo("\n  No symbols found.")
        update_manifest(root, cfg, manifest, candidates, all_nodes, {})
        return

    total_symbols = len(all_nodes)
    click.echo(f"\n    {total_symbols} symbols across {len(candidates)} files  ({cached_count} from cache)\n")

    # ── Phase 2: Cross-reference (with existing nodes for complete called_by) ──
    click.echo("  Cross-referencing calls")
    if not force and manifest.last_indexed_commit is not None:
        existing_nodes = load_existing_nodes(root, manifest, cfg)
        cross_reference(existing_nodes + all_nodes)
    else:
        cross_reference(all_nodes)
    linked = sum(1 for n in all_nodes if n.called_by)
    click.echo(f"    {linked} symbols linked via call graph\n")

    # ── Phase 3: LLM descriptions ─────────────────────────────────────────────
    from indexer.indexing import load_cached_descriptions, save_cached_descriptions, load_cached_file_descriptions, save_cached_file_descriptions
    cached_descs = load_cached_descriptions(root)
    new_nodes = [n for n in all_nodes if n.id not in cached_descs]

    file_nodes: dict[str, list] = {}
    for node in all_nodes:
        file_nodes.setdefault(node.file, []).append(node)
    cached_file_descs = load_cached_file_descriptions(root)
    new_file_nodes = {f: nodes for f, nodes in file_nodes.items() if f not in cached_file_descs}

    from concurrent.futures import ThreadPoolExecutor, as_completed as _as_completed

    new_descriptions = {}
    new_file_descriptions = {}
    with ThreadPoolExecutor(max_workers=2) as _desc_pool:
        _desc_futures = {}
        if new_nodes:
            new_batches = build_batches(new_nodes, cfg)
            click.echo(f"  Describing symbols  ({len(new_batches)} LLM batch{'es' if len(new_batches) != 1 else ''}, concurrent)")
            _desc_futures[_desc_pool.submit(describe_nodes, new_batches, cfg)] = "symbols"
        if new_file_nodes:
            click.echo(f"  Describing modules  ({len(new_file_nodes)} new files)  ...", nl=False)
            _desc_futures[_desc_pool.submit(describe_files, new_file_nodes, cfg)] = "files"
        for _fut in _as_completed(_desc_futures):
            _label = _desc_futures[_fut]
            try:
                _result = _fut.result()
            except Exception as e:
                logger.warning("Parallel description failed for %s: %s", _label, e)
                _result = {}
            if _label == "symbols":
                new_descriptions = _result
            else:
                new_file_descriptions = _result

    if new_file_nodes:
        click.echo(f"  {sum(1 for v in new_file_descriptions.values() if v)}/{len(new_file_nodes)} described\n")

    if new_descriptions:
        save_cached_descriptions(root, new_descriptions)
    if new_file_descriptions:
        save_cached_file_descriptions(root, new_file_descriptions)

    descriptions = {**cached_descs, **new_descriptions}
    for n in all_nodes:
        descriptions.setdefault(n.id, "")
    file_descriptions = {**cached_file_descs, **new_file_descriptions}
    for f in file_nodes:
        file_descriptions.setdefault(f, "")
    filled = sum(1 for v in descriptions.values() if v)
    filled_files = sum(1 for v in file_descriptions.values() if v)

    # ── Phase 5: Deep enrichment + wiki pages ─────────────────────────────────
    page_enrichments: dict[str, dict] = {}
    groups = density_group(candidates, merge_threshold=cfg.merge_threshold)
    if not skip_deep:
        click.echo(f"\n  Deep enrichment  ({len(groups)} pages, concurrent)  —  narrative + flows + constraints")
        group_nodes: dict[str, list] = {}
        for node in all_nodes:
            group = groups.get(node.file, node.file)
            group_nodes.setdefault(group, []).append(node)
        pages_args = [
            (group_label, list({n.file for n in nodes}), nodes, descriptions)
            for group_label, nodes in group_nodes.items()
        ]
        page_enrichments = deep_enrich_pages(pages_args, cfg)
        for group_label, enrichment in page_enrichments.items():
            parts = []
            if enrichment["narrative"]: parts.append("narrative")
            if enrichment["data_flows"]: parts.append(f"{len(enrichment['data_flows'])} flows")
            if enrichment["constraints"]: parts.append(f"{len(enrichment['constraints'])} constraints")
            click.echo(f"    {group_label}  {', '.join(parts) or 'empty'}")
        click.echo()

    click.echo("  Writing wiki")
    index_entries, groups = write_wiki_pages(
        root, cfg, candidates, all_nodes, descriptions, file_descriptions,
        page_enrichments, skip_deep, precomputed_groups=groups,
    )
    for entry in index_entries:
        page_name = entry.path.split("/")[-1]
        symbol_count = sum(1 for n in all_nodes if any(n.file == f for f in entry.covers.split(", ")))
        click.echo(f"    ✓  {entry.path}  ({symbol_count} symbols)")

    # ── Phase 6: INDEX + skill ────────────────────────────────────────────────
    index_overview = ""
    index_flows: list[str] = []
    if not skip_deep:
        click.echo("\n  Deep enrichment  (INDEX overview)  ...", nl=False)
        skill_pages_for_deep = [
            {"label": Path(e.path).stem, "covers": e.covers, "entry_points": e.entry_points}
            for e in index_entries
        ]
        idx_enrichment = deep_enrich_index(skill_pages_for_deep, cfg)
        index_overview = idx_enrichment.get("overview", "")
        index_flows = idx_enrichment.get("flows", [])
        click.echo(f"  {'overview + ' + str(len(index_flows)) + ' flows' if index_overview else 'empty'}\n")

    write_index_and_skill(
        root, cfg, index_entries, page_enrichments,
        index_overview, index_flows, total_symbols, len(candidates),
    )
    click.echo(f"    ✓  {cfg.wiki_dir}/INDEX.md")
    click.echo(f"    ✓  .indexer/skills/codebase.md")

    # ── Update manifest ────────────────────────────────────────────────────────
    removed = manifest.removed_files(root, all_git_files)
    update_manifest(root, cfg, manifest, candidates, all_nodes, groups)

    # ── Auto-stage ALL generated files (pre-commit hook) ──────────────────────
    if staged and is_git_repo(root):
        git_env_cli = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        r = subprocess.run(
            ["git", "add",
             cfg.wiki_dir,
             ".indexer/manifest.json",
             ".indexer/skills/codebase.md",
             ".gitignore"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            env=git_env_cli,
        )
        if r.returncode != 0:
            click.echo(f"  Warning: git add failed: {r.stderr.strip()}", err=True)
        else:
            click.echo(f"\n  Staged wiki + manifest + skill file")

    # ── Commit message synthesis ───────────────────────────────────────────────
    if cfg.synthesize_commit_message and staged:
        click.echo("  Synthesizing commit message  ...", nl=False)
        msg = synthesize_commit_message(candidates, descriptions, cfg)
        if msg:
            click.echo(f"\n\n  Suggested commit message:\n    {msg}\n")
        else:
            click.echo("  (skipped)\n")

    # ── Phase 7: Vector store ────────────────────────────────────────────────
    click.echo("\n  Embedding + vector store")
    try:
        branch = current_branch(root) or ""
        upsert_vectors(root, cfg, manifest, all_nodes, descriptions, removed_files=removed, branch=branch)
        click.echo(f"    ✓  {total_symbols} vectors upserted")
    except Exception as e:
        logger.error("Vector store indexing failed: %s", e)
        click.echo(f"    ⚠  Skipped vector store (error: {e})")

    click.echo(f"\n  Done  —  {len(index_entries)} wiki page(s)  —  {total_symbols} symbols indexed\n")


@main.command()
def status():
    """Show last indexed commit, stale files, manifest stats."""
    root = Path.cwd()
    cfg = load_config(root)
    manifest = load_manifest(root)

    click.echo(f"Last indexed commit: {manifest.last_indexed_commit or 'never'}")
    click.echo(f"Indexed at:          {manifest.indexed_at or 'n/a'}")
    click.echo(f"Tracked files:       {len(manifest.files)}")

    if is_git_repo(root):
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]
        stale = manifest.stale_files(root, all_files)
        click.echo(f"Stale files:         {len(stale)}")
        if stale:
            for f in stale[:10]:
                click.echo(f"  {f}")


@main.group()
def hook():
    """Manage the pre-commit hook."""
    pass


@hook.command("install")
def hook_install():
    """Install the pre-commit hook in the current repo."""
    root = Path.cwd()
    cfg = load_config(root)
    install_hook(root, skip_deep=not cfg.deep_hook)
    mode = "--staged --skip-deep" if not cfg.deep_hook else "--staged"
    click.echo(f"Pre-commit hook installed  (repo-wiki run {mode})")


@hook.command("remove")
def hook_remove():
    """Remove the pre-commit hook from the current repo."""
    root = Path.cwd()
    remove_hook(root)
    click.echo("Pre-commit hook removed.")


@main.command()
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "streamable-http"]), help="MCP transport mode")
@click.option("--host", default="0.0.0.0", help="Host for streamable-http mode")
@click.option("--port", default=8000, type=int, help="Port for streamable-http mode")
@click.option("--api", default=None, help="REST API URL for multi-repo mode (e.g. http://localhost:7654)")
def serve(transport: str, host: str, port: int, api: str | None):
    """Start the repo-wiki MCP server for semantic code search."""
    mcp_api_key = os.environ.get("MCP_API_KEY", "")
    if api:
        from indexer.mcp_server import create_api_server
        server = create_api_server(api, mcp_api_key=mcp_api_key)
        click.echo(f"MCP server started in multi-repo mode (API: {api})")
    else:
        from indexer.mcp_server import create_server
        root = Path.cwd()
        server = create_server(root, mcp_api_key=mcp_api_key)
        click.echo(f"MCP server started in single-repo mode ({root})")

    server.settings.host = host
    server.settings.port = port

    if transport == "streamable-http":
        server.run(transport="streamable-http")
    else:
        server.run(transport="stdio")


@main.command()
@click.option("--host", default="0.0.0.0", help="Bind host")
@click.option("--port", default=8765, type=int, help="Bind port")
@click.option("--repos-dir", default=None, help="Directory to store cloned repos (default: /tmp/repo-wiki_repos)")
@click.option("--repo", multiple=True, help="Register repo as NAME=PATH (e.g. backend=/path/to/repo). Can be repeated.")
@click.option("--auto-detect", is_flag=True, help="Auto-detect repos from subdirectories containing .indexer.toml")
def serve_api(host: str, port: int, repos_dir: str | None, repo: tuple[str, ...], auto_detect: bool):
    """Start a REST API server for remote semantic code search across multiple repos."""
    import uvicorn
    from indexer.rest_api import create_app

    repos_map: dict[str, Path] = {}

    for r in repo:
        if "=" not in r:
            click.echo(f"Invalid repo format: '{r}'. Use NAME=PATH (e.g. backend=/path/to/repo)")
            return
        name, path = r.split("=", 1)
        p = Path(path).resolve()
        if not p.exists():
            click.echo(f"Repo path does not exist: {p}")
            return
        repos_map[name] = p

    if auto_detect:
        cwd = Path.cwd()
        for sub in cwd.iterdir():
            if sub.is_dir() and (sub / ".indexer.toml").exists():
                name = sub.name
                if name not in repos_map:
                    repos_map[name] = sub.resolve()

    repos_dir_path = Path(repos_dir).resolve() if repos_dir else None

    if not repos_map and not repos_dir_path:
        root = Path.cwd()
        if (root / ".indexer.toml").exists():
            repos_map["default"] = root
        else:
            click.echo("No repos registered. Use --repo NAME=PATH, --repos-dir, or run from an indexed repo.")

    app = create_app(repos=repos_map, repos_dir=repos_dir_path)

    initial_count = len(repos_map)
    click.echo(f"\n  repo-wiki REST API  —  {initial_count} repo(s) pre-registered")
    if repos_dir_path:
        click.echo(f"    Cloned repos will be stored in: {repos_dir_path}")
    for name, path in repos_map.items():
        click.echo(f"    {name}  →  {path}")
    click.echo(f"\n  Listening on http://{host}:{port}")
    click.echo(f"\n  Endpoints:")
    click.echo(f"    POST /register   — clone & index a remote repo")
    click.echo(f"    POST /unregister — remove a repo from registry")
    click.echo(f"    POST /search     — semantic symbol search")
    click.echo(f"    POST /trace      — call graph tracing")
    click.echo(f"    POST /source     — get source code context")
    click.echo(f"    GET  /repos      — list registered repos")
    click.echo(f"    GET  /health     — health check")
    click.echo(f"\n  Example: curl -X POST http://{host}:{port}/register -H 'Content-Type: application/json' -d '{{\"url\": \"https://github.com/org/repo.git\", \"token\": \"ghp_xxx\"}}'\n")

    uvicorn.run(app, host=host, port=port)


CACHE_GITIGNORE_ENTRY = ".indexer/cache/"
VECTOR_GITIGNORE_ENTRY = ".indexer/vector_db/"

CACHE_GITIGNORE_ENTRIES = [CACHE_GITIGNORE_ENTRY, VECTOR_GITIGNORE_ENTRY]


def _ensure_cache_gitignore(root: Path, verbose: bool = False) -> None:
    gitignore = root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        existing_lines = {line.strip() for line in content.splitlines()}
        missing = [e for e in CACHE_GITIGNORE_ENTRIES if e not in existing_lines]
        if not missing:
            return
        updated = content.rstrip() + "\n\n# repo-wiki\n" + "\n".join(missing) + "\n"
        gitignore.write_text(updated)
        if verbose:
            for e in missing:
                click.echo(f"Added {e} to .gitignore")
    else:
        gitignore.write_text(f"# repo-wiki\n" + "\n".join(CACHE_GITIGNORE_ENTRIES) + "\n")
        if verbose:
            for e in CACHE_GITIGNORE_ENTRIES:
                click.echo(f"Created .gitignore with {e}")


def _is_indexable(path: str, cfg: Config) -> bool:
    p = Path(path)
    if p.suffix not in {".py", ".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx", ".go", ".rs", ".java", ".rb"}:
        return False
    for pattern in cfg.ignore:
        if any(fnmatch(part, pattern) for part in p.parts):
            return False
        if fnmatch(path, pattern):
            return False
    return True
