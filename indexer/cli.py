# indexer/cli.py
from __future__ import annotations
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

import click

from indexer.config import load_config, save_config
from indexer.git import is_git_repo
from indexer.git_snapshot import STAGED_REVISION, WORKTREE_REVISION
from indexer.hooks import install_hook, remove_hook
from indexer.repository_service import RepositoryService, default_branch

CLAUDEMD_SNIPPET = """
## Codebase Navigation

This repo is indexed with repo-wiki. Before reading any source file or answering any code question:

1. Load `.indexer/skills/codebase.md` as a skill — it contains the full navigation workflow.
2. Read `wiki/INDEX.md` for the system overview and module map.
3. Match the question to a wiki page, look up symbols there, and only read source when you know the exact file and line range.

Do not read source files speculatively. The wiki gives you structure and relationships in a fraction of the tokens.

- Wiki pages: `wiki/` — grouped by logical density, not directory structure
- Index state: `.indexer/state/repository-index.sqlite3` — transactional generations
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
        install_hook(root)
        mode = "--staged"
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
@click.option("--enrich", is_flag=True, help="Publish an embedding enrichment revision after the structural generation")
def run(staged: bool, enrich: bool):
    """Index the codebase and generate wiki pages."""
    root = Path.cwd()
    cfg = load_config(root)
    _ensure_cache_gitignore(root)
    branch = default_branch(root)
    service = RepositoryService(
        root.name,
        root,
        branch,
        config=cfg,
    )
    result = service.sync(
        revision=STAGED_REVISION if staged else WORKTREE_REVISION,
        enrich=enrich,
    )
    projection = service.project()
    sync = result["sync"]

    click.echo(
        f"\n  {sync['status']} generation {sync['generation']}  —  "
        f"{projection['pages']} wiki page(s)  —  "
        f"{projection['symbols']} symbols  —  "
        f"{sync['parsed_blobs']} parsed blob(s)\n"
    )
    if result["degradation"]:
        click.echo(f"  Enrichment degraded: {result['degradation']}", err=True)


@main.command()
def status():
    """Show the current generation and workspace freshness."""
    root = Path.cwd()
    service = RepositoryService(root.name, root, default_branch(root))
    report = service.inspect(revision=WORKTREE_REVISION)
    click.echo(f"Generation:           {report['generation'] or 'never'}")
    click.echo(f"Indexed tree:         {report['indexed_tree'] or 'n/a'}")
    click.echo(f"Indexed files:        {report['indexed_files']}")
    click.echo(f"Symbols:              {report['symbols']}")
    click.echo(f"Dense state:          {report['dense_state']}")
    click.echo(f"Stale files:          {report['stale_file_count']}")
    for file_path in report["stale_files"][:10]:
        click.echo(f"  {file_path}")


@main.command()
@click.option("--retain-generations", default=2, type=click.IntRange(min=1))
def maintain(retain_generations: int):
    """Recover interrupted jobs, collect unreachable state, and verify SQLite."""
    root = Path.cwd()
    service = RepositoryService(root.name, root, default_branch(root))
    report = service.index.maintain(retain_generations=retain_generations)
    click.echo(f"Retained generations:    {report.retained_generations}")
    click.echo(f"Recovered jobs:          {report.recovered_jobs}")
    click.echo(f"Deleted generations:     {report.deleted_generations}")
    click.echo(f"Deleted revisions:       {report.deleted_revisions}")
    click.echo(f"Deleted parse artifacts: {report.deleted_artifacts}")
    click.echo(f"Deleted embeddings:      {report.deleted_embeddings}")
    click.echo(f"Deleted Git objects:     {report.deleted_snapshot_objects}")
    click.echo(f"Reclaimed SQLite pages:  {report.reclaimed_pages}")
    click.echo(f"SQLite integrity:        {'ok' if report.integrity.ok else 'failed'}")


@main.group()
def agent():
    """Run local Agent code-location workflows."""
    pass


@agent.command("context")
@click.option("--symbol-id", required=True, help="Component ID to inspect, e.g. src/auth.py::validate_token")
@click.option("--padding", default=8, type=int, help="Source context padding")
def agent_context(symbol_id: str, padding: int):
    """Print an edit-context bundle for a symbol."""
    from indexer.agent_context import get_edit_context

    root = Path.cwd()
    cfg = load_config(root)
    click.echo(_json_dumps(get_edit_context(symbol_id, cfg, root, padding=padding)))


@agent.command("verify")
@click.option("--diff-file", type=click.Path(exists=True, dir_okay=False), help="Read a git diff from this file")
@click.option("--changed-file", multiple=True, help="Changed file path. Can be repeated.")
def agent_verify(diff_file: str | None, changed_file: tuple[str, ...]):
    """Suggest verification after an Agent edit."""
    from indexer.agent_diff import post_edit_verify

    root = Path.cwd()
    cfg = load_config(root)
    diff = Path(diff_file).read_text(encoding="utf-8", errors="replace") if diff_file else ""
    click.echo(_json_dumps(post_edit_verify(cfg, root, diff=diff, changed_files=list(changed_file) or None)))


@agent.command("plan")
@click.option("--goal", required=True, help="Change goal")
@click.option("--symbol-id", required=True, help="Target component ID")
def agent_plan(goal: str, symbol_id: str):
    """Print an Agent change plan."""
    from indexer.agent_context import change_plan

    root = Path.cwd()
    cfg = load_config(root)
    click.echo(_json_dumps(change_plan(goal, symbol_id, cfg, root)))


@agent.command("diagnose")
def agent_diagnose():
    """Print local index health diagnostics."""
    from indexer.agent_diagnostics import diagnose_index

    root = Path.cwd()
    cfg = load_config(root)
    click.echo(_json_dumps(diagnose_index(root, cfg)))


@agent.command("capabilities")
def agent_capabilities():
    """Print the Agent tool manifest."""
    from indexer.agent_protocol import agent_capabilities_manifest

    click.echo(_json_dumps(agent_capabilities_manifest()))


@agent.command("schema")
def agent_schema():
    """Print the machine-readable Agent API schema."""
    from indexer.agent_protocol import agent_schema

    click.echo(_json_dumps(agent_schema()))


@main.group()
def hook():
    """Manage the pre-commit hook."""
    pass


@hook.command("install")
def hook_install():
    """Install the pre-commit hook in the current repo."""
    root = Path.cwd()
    cfg = load_config(root)
    install_hook(root)
    mode = "--staged"
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


STATE_GITIGNORE_ENTRY = ".indexer/state/"

CACHE_GITIGNORE_ENTRIES = [
    STATE_GITIGNORE_ENTRY,
]


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


def _json_dumps(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
