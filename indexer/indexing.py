from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

from indexer.ast_parser import ASTNode, parse_file, load_cached_nodes, save_cached_nodes, compute_hash_short
from indexer.config import Config
from indexer.grouper import density_group
from indexer.llm import describe_nodes, describe_files, deep_enrich_pages, deep_enrich_index
from indexer.manifest import Manifest, FileEntry, compute_hash, load_manifest, save_manifest
from indexer.wiki import (
    PageContext, IndexEntry, TEMPLATES_DIR,
    build_page, build_index, write_page, write_index,
    sanitize_group_label,
)
from indexer.git import all_tracked_files, current_commit, is_git_repo, changed_files_since


def cross_reference(all_nodes: list[ASTNode]) -> None:
    call_index: dict[str, list[str]] = {}
    for node in all_nodes:
        for callee_name in node.calls:
            call_index.setdefault(callee_name, []).append(node.id)
    for node in all_nodes:
        bare_name = node.id.split("::")[-1]
        node.called_by = call_index.get(bare_name, [])


def load_existing_nodes(root: Path, manifest: Manifest, cfg: Config) -> list[ASTNode]:
    existing_nodes: list[ASTNode] = []
    for rel_path, entry in manifest.files.items():
        abs_path = root / rel_path
        if not abs_path.exists():
            continue
        file_hash = compute_hash_short(abs_path)
        cached = load_cached_nodes(root, file_hash)
        if cached is not None:
            existing_nodes.extend(cached)
    return existing_nodes


def parse_candidates(
    root: Path,
    candidates: list[str],
    cfg: Config,
    use_cache: bool = True,
    progress_callback=None,
) -> list[ASTNode]:
    all_nodes: list[ASTNode] = []
    total = len(candidates)
    for i, rel_path in enumerate(candidates, 1):
        abs_path = root / rel_path
        file_hash = compute_hash_short(abs_path)

        if use_cache:
            cached = load_cached_nodes(root, file_hash)
            if cached is not None:
                all_nodes.extend(cached)
                if progress_callback:
                    progress_callback(i, total, rel_path, cached=True)
                continue

        nodes = parse_file(abs_path, root)
        if use_cache:
            save_cached_nodes(root, file_hash, nodes)
        all_nodes.extend(nodes)
        if progress_callback:
            progress_callback(i, total, rel_path, cached=False, count=len(nodes))
    return all_nodes


def build_batches(all_nodes: list[ASTNode], cfg: Config) -> list[list[ASTNode]]:
    batch, batch_size = [], 0
    batches = []
    for node in all_nodes:
        node_size = len(node.docstring or "") + len(" ".join(node.calls)) + 50
        if batch_size + node_size > cfg.max_tokens_per_batch and batch:
            batches.append(batch)
            batch, batch_size = [], 0
        batch.append(node)
        batch_size += node_size
    if batch:
        batches.append(batch)
    return batches


def write_wiki_pages(
    root: Path,
    cfg: Config,
    candidates: list[str],
    all_nodes: list[ASTNode],
    descriptions: dict[str, str],
    file_descriptions: dict[str, str],
    page_enrichments: dict[str, dict],
    skip_deep: bool = False,
) -> tuple[list[IndexEntry], dict[str, str]]:
    groups = density_group(candidates, merge_threshold=cfg.merge_threshold)
    group_nodes: dict[str, list] = {}
    for node in all_nodes:
        group = groups.get(node.file, node.file)
        group_nodes.setdefault(group, []).append(node)

    wiki_dir = root / cfg.wiki_dir
    index_entries = []

    for group_label, nodes in group_nodes.items():
        enrichment = page_enrichments.get(group_label, {})
        ctx = PageContext(
            group_label=group_label,
            files=list({n.file for n in nodes}),
            nodes=nodes,
            descriptions=descriptions,
            file_descriptions=file_descriptions,
            narrative=enrichment.get("narrative", ""),
            data_flows=enrichment.get("data_flows", []),
            constraints=enrichment.get("constraints", []),
        )
        content = build_page(ctx)
        page_path = write_page(wiki_dir, group_label, content)
        entry_points = [n.id.split("::")[-1] for n in nodes if not n.called_by]
        index_entries.append(IndexEntry(
            path=str(page_path.relative_to(root)),
            covers=", ".join(sorted({n.file for n in nodes})),
            entry_points=entry_points,
        ))

    return index_entries, groups


def write_index_and_skill(
    root: Path,
    cfg: Config,
    index_entries: list[IndexEntry],
    page_enrichments: dict[str, dict],
    index_overview: str,
    index_flows: list[str],
    total_symbols: int,
    total_files: int,
) -> None:
    wiki_dir = root / cfg.wiki_dir
    commit = current_commit(root) or "unknown"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    index_content = build_index(index_entries, commit, today, overview=index_overview, flows=index_flows)
    write_index(wiki_dir, index_content)

    from jinja2 import Environment, FileSystemLoader
    skill_dir = root / ".indexer" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
    skill_pages = [
        {
            "label": e.path.split("/")[-1].replace(".md", ""),
            "path": e.path,
            "covers": e.covers,
            "entry_points": e.entry_points[:5],
            "enrichment": page_enrichments.get(e.path.split("/")[-1].replace(".md", ""), {}),
        }
        for e in index_entries
    ]
    skill_content = env.get_template("skill.md.j2").render(
        wiki_dir=cfg.wiki_dir,
        pages=skill_pages,
        overview=index_overview,
        key_flows=index_flows,
        total_symbols=total_symbols,
        total_files=total_files,
        commit=commit,
        indexed_date=today,
    )
    (skill_dir / "codebase.md").write_text(skill_content)


def update_manifest(
    root: Path,
    cfg: Config,
    manifest: Manifest,
    candidates: list[str],
    all_nodes: list[ASTNode],
    groups: dict[str, str],
) -> None:
    commit = current_commit(root) or "unknown"
    now = datetime.now(timezone.utc).isoformat()
    for rel_path in candidates:
        abs_path = root / rel_path
        if abs_path.exists():
            file_hash = compute_hash(abs_path)
            group = groups.get(rel_path, rel_path)
            safe_group = sanitize_group_label(group)
            manifest.files[rel_path] = FileEntry(
                hash=file_hash,
                wiki_page=f"{cfg.wiki_dir}/{safe_group}.md",
                component_ids=[n.id for n in all_nodes if n.file == rel_path],
            )
    manifest.last_indexed_commit = commit
    manifest.indexed_at = now

    if is_git_repo(root):
        tracked = set(all_tracked_files(root))
        stale_keys = [k for k in manifest.files if k not in tracked]
        for k in stale_keys:
            del manifest.files[k]

    save_manifest(root, manifest)


def upsert_vectors(
    root: Path,
    cfg: Config,
    manifest: Manifest,
    all_nodes: list[ASTNode],
    descriptions: dict[str, str],
    removed_files: list[str] | None = None,
    branch: str = "",
) -> None:
    from indexer.embedding import embed_nodes
    from indexer.vector_store import upsert_nodes as vs_upsert, delete_by_files as vs_delete

    if removed_files is None:
        removed_files = manifest.removed_files(root, all_tracked_files(root) if is_git_repo(root) else [])
    if removed_files:
        vs_delete(removed_files, cfg.vector_store, root, branch=branch)

    vectors = embed_nodes(all_nodes, descriptions, cfg.embedding)
    vs_upsert(all_nodes, vectors, descriptions, cfg.vector_store, root, dim=cfg.embedding.dimensions, branch=branch)
