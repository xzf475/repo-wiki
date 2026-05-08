from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from indexer.ast_parser import ASTNode, parse_file, load_cached_nodes, save_cached_nodes, compute_hash_short
from indexer.config import Config
from indexer.embedding import embed_nodes, _build_text
from indexer.grouper import density_group
from indexer.llm import describe_nodes, describe_files, deep_enrich_pages, deep_enrich_index
from indexer.manifest import Manifest, FileEntry, compute_hash, load_manifest, save_manifest
from indexer.vector_store import upsert_nodes as vs_upsert, delete_by_files as vs_delete
from indexer.wiki import (
    PageContext, IndexEntry, TEMPLATES_DIR,
    build_page, build_index, write_page, write_index,
    sanitize_group_label,
)
from indexer.git import all_tracked_files, current_commit, is_git_repo, changed_files_since

logger = logging.getLogger(__name__)


def _desc_cache_path(root: Path) -> Path:
    p = root / ".indexer" / "cache" / "descriptions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_cached_descriptions(root: Path) -> dict[str, str]:
    p = _desc_cache_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cached_descriptions(root: Path, descriptions: dict[str, str]) -> None:
    p = _desc_cache_path(root)
    try:
        existing = load_cached_descriptions(root)
        existing.update(descriptions)
        p.write_text(json.dumps(existing, indent=2))
    except OSError as e:
        logger.warning("Failed to save description cache: %s", e)


def _file_desc_cache_path(root: Path) -> Path:
    p = root / ".indexer" / "cache" / "file_descriptions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_cached_file_descriptions(root: Path) -> dict[str, str]:
    p = _file_desc_cache_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cached_file_descriptions(root: Path, descriptions: dict[str, str]) -> None:
    p = _file_desc_cache_path(root)
    try:
        existing = load_cached_file_descriptions(root)
        existing.update(descriptions)
        p.write_text(json.dumps(existing, indent=2))
    except OSError as e:
        logger.warning("Failed to save file description cache: %s", e)


def cross_reference(all_nodes: list[ASTNode]) -> None:
    call_index: dict[str, list[str]] = {}
    file_call_index: dict[tuple[str, str], list[str]] = {}
    for node in all_nodes:
        for callee_name in node.calls:
            call_index.setdefault(callee_name, []).append(node.id)
            file_call_index.setdefault((node.file, callee_name), []).append(node.id)
    for node in all_nodes:
        bare_name = node.id.split("::")[-1]
        same_file_callers = file_call_index.get((node.file, bare_name), [])
        global_callers = call_index.get(bare_name, [])
        if same_file_callers:
            seen = set(same_file_callers)
            node.called_by = same_file_callers + [c for c in global_callers if c not in seen]
        else:
            node.called_by = global_callers


def load_existing_nodes(root: Path, manifest: Manifest, cfg: Config) -> list[ASTNode]:
    existing_nodes: list[ASTNode] = []
    for rel_path, entry in manifest.files.items():
        abs_path = root / rel_path
        if not abs_path.exists():
            continue
        short_hash = entry.hash[7:7+16] if entry.hash and entry.hash.startswith("sha256:") else (entry.hash[:16] if entry.hash else compute_hash_short(abs_path))
        cached = load_cached_nodes(root, short_hash)
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

    uncached = []
    if use_cache:
        for i, rel_path in enumerate(candidates, 1):
            abs_path = root / rel_path
            file_hash = compute_hash_short(abs_path)
            cached = load_cached_nodes(root, file_hash)
            if cached is not None:
                all_nodes.extend(cached)
                if progress_callback:
                    progress_callback(i, total, rel_path, cached=True)
            else:
                uncached.append((i, rel_path, abs_path, file_hash))
    else:
        uncached = [(i, rel_path, root / rel_path, compute_hash_short(root / rel_path))
                    for i, rel_path in enumerate(candidates, 1)]

    if uncached:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(parse_file, item[2], root): item for item in uncached}
            for future in as_completed(futures):
                item = futures[future]
                i, rel_path, abs_path, file_hash = item
                try:
                    nodes = future.result()
                except Exception as e:
                    logger.warning("Failed to parse %s: %s", rel_path, e)
                    continue
                if use_cache:
                    save_cached_nodes(root, file_hash, nodes)
                all_nodes.extend(nodes)
                if progress_callback:
                    progress_callback(i, total, rel_path, cached=False, count=len(nodes))

    return all_nodes


def build_batches(all_nodes: list[ASTNode], cfg: Config) -> list[list[ASTNode]]:
    batch, batch_size = [], 0
    batches = []
    char_budget = cfg.max_tokens_per_batch * 3
    for node in all_nodes:
        node_size = len(node.id) + len(node.type) + len(node.docstring or "") + len(" ".join(node.calls[:15])) + len(" ".join(node.called_by[:15] if node.called_by else [])) + 80
        if batch_size + node_size > char_budget and batch:
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
    precomputed_groups: dict[str, str] | None = None,
) -> tuple[list[IndexEntry], dict[str, str]]:
    groups = precomputed_groups if precomputed_groups is not None else density_group(candidates, merge_threshold=cfg.merge_threshold)
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
            group_label=group_label,
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
            "label": Path(e.path).stem,
            "path": e.path,
            "covers": e.covers,
            "entry_points": e.entry_points[:5],
            "enrichment": page_enrichments.get(e.group_label, {}),
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
    file_to_nodes: dict[str, list[str]] = {}
    for n in all_nodes:
        file_to_nodes.setdefault(n.file, []).append(n.id)
    for rel_path in candidates:
        abs_path = root / rel_path
        if abs_path.exists():
            file_hash = compute_hash(abs_path)
            group = groups.get(rel_path, rel_path)
            safe_group = sanitize_group_label(group)
            manifest.files[rel_path] = FileEntry(
                hash=file_hash,
                wiki_page=f"{cfg.wiki_dir}/{safe_group}.md",
                component_ids=file_to_nodes.get(rel_path, []),
            )
    manifest.last_indexed_commit = commit
    manifest.indexed_at = now

    if is_git_repo(root):
        tracked = set(all_tracked_files(root))
        stale_keys = [k for k in manifest.files if k not in tracked]
    else:
        stale_keys = [k for k in manifest.files if not (root / k).exists()]
    for k in stale_keys:
        del manifest.files[k]

    save_manifest(root, manifest)


def _embedding_cache_path(root: Path) -> Path:
    p = root / ".indexer" / "cache" / "embeddings.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _embedding_cache_sig(node: ASTNode, description: str) -> str:
    text = _build_text(node, description)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_cached_embeddings(root: Path) -> dict[str, dict]:
    p = _embedding_cache_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cached_embeddings(root: Path, entries: dict[str, dict], current_node_ids: set[str] | None = None) -> None:
    p = _embedding_cache_path(root)
    try:
        existing = load_cached_embeddings(root)
        existing.update(entries)
        if current_node_ids is not None:
            stale = [k for k in existing if k not in current_node_ids]
            for k in stale:
                del existing[k]
        p.write_text(json.dumps(existing))
    except OSError as e:
        logger.warning("Failed to save embedding cache: %s", e)


def upsert_vectors(
    root: Path,
    cfg: Config,
    manifest: Manifest,
    all_nodes: list[ASTNode],
    descriptions: dict[str, str],
    removed_files: list[str] | None = None,
    branch: str = "",
) -> None:
    if removed_files is None:
        if is_git_repo(root):
            tracked = all_tracked_files(root)
        else:
            tracked = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)]
        removed_files = manifest.removed_files(root, tracked)
    if removed_files:
        vs_delete(removed_files, cfg.vector_store, root, branch=branch)

    seen_ids: set[str] = set()
    deduped_nodes: list[ASTNode] = []
    for node in all_nodes:
        if node.id not in seen_ids:
            seen_ids.add(node.id)
            deduped_nodes.append(node)
    if len(deduped_nodes) < len(all_nodes):
        logger.warning("Deduplicated nodes: %d -> %d", len(all_nodes), len(deduped_nodes))
    all_nodes = deduped_nodes

    cached_emb = load_cached_embeddings(root)
    hit_vectors: dict[str, list[float]] = {}
    miss_nodes: list[ASTNode] = []

    for node in all_nodes:
        sig = _embedding_cache_sig(node, descriptions.get(node.id, ""))
        entry = cached_emb.get(node.id)
        if entry and entry.get("sig") == sig and entry.get("vec"):
            hit_vectors[node.id] = entry["vec"]
        else:
            miss_nodes.append(node)

    if miss_nodes:
        new_vectors = embed_nodes(miss_nodes, descriptions, cfg.embedding)
        new_cache_entries = {}
        for node in miss_nodes:
            vec = new_vectors.get(node.id)
            if vec:
                sig = _embedding_cache_sig(node, descriptions.get(node.id, ""))
                new_cache_entries[node.id] = {"sig": sig, "vec": vec}
        save_cached_embeddings(root, new_cache_entries, current_node_ids=seen_ids)
        hit_vectors.update(new_vectors)
    else:
        logger.info("Embedding cache hit: %d/%d nodes, 0 API calls", len(hit_vectors), len(all_nodes))
        if cached_emb and set(cached_emb.keys()) - seen_ids:
            save_cached_embeddings(root, {}, current_node_ids=seen_ids)

    if len(hit_vectors) < len(all_nodes):
        logger.warning("Embedding incomplete: %d/%d vectors available", len(hit_vectors), len(all_nodes))

    vs_upsert(all_nodes, hit_vectors, descriptions, cfg.vector_store, root, dim=cfg.embedding.dimensions, branch=branch)
