from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from indexer.ast_parser import ASTNode, parse_file, load_cached_nodes, save_cached_nodes, compute_hash_short
from indexer.config import Config
from indexer.embedding import embed_nodes, compute_embedding_sig
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


def compute_ast_sig(node: ASTNode) -> str:
    parts = [node.type, str(node.line_start), str(node.line_end), node.docstring or ""]
    parts.extend(node.calls[:15])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def _atomic_write_json(path: Path, data: object) -> None:
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, separators=(",", ":")))
        tmp.replace(path)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise e


def _desc_cache_dir(root: Path) -> Path:
    d = root / ".indexer" / "cache" / "desc"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _desc_shard_key(node_id: str) -> str:
    return node_id[0].lower() if node_id else "0"


def load_cached_descriptions(root: Path) -> dict[str, dict]:
    d = _desc_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "descriptions.json"
    if legacy.exists() and not any(d.iterdir()):
        try:
            raw = json.loads(legacy.read_text())
            result = {}
            for k, v in raw.items():
                if isinstance(v, str):
                    result[k] = {"desc": v, "sig": ""}
                elif isinstance(v, dict):
                    result[k] = v
            return result
        except (json.JSONDecodeError, OSError):
            pass
    result = {}
    for shard_file in d.glob("*.json"):
        try:
            data = json.loads(shard_file.read_text())
            for k, v in data.items():
                if isinstance(v, str):
                    result[k] = {"desc": v, "sig": ""}
                elif isinstance(v, dict):
                    result[k] = v
        except (json.JSONDecodeError, OSError):
            pass
    return result


def save_cached_descriptions(root: Path, descriptions: dict[str, str], current_node_ids: set[str] | None = None, sigs: dict[str, str] | None = None) -> None:
    d = _desc_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "descriptions.json"
    try:
        by_shard: dict[str, dict] = {}
        for node_id, desc in descriptions.items():
            shard = _desc_shard_key(node_id)
            sig = sigs.get(node_id, "") if sigs else ""
            by_shard.setdefault(shard, {})[node_id] = {"desc": desc, "sig": sig}

        if current_node_ids is not None:
            for shard_file in d.glob("*.json"):
                try:
                    data = json.loads(shard_file.read_text())
                except (json.JSONDecodeError, OSError):
                    continue
                shard = shard_file.stem
                stale = [k for k in data if k not in current_node_ids]
                if stale:
                    for k in stale:
                        del data[k]
                if stale or shard in by_shard:
                    by_shard[shard] = data
                    for node_id, desc in descriptions.items():
                        if _desc_shard_key(node_id) == shard:
                            sig = sigs.get(node_id, "") if sigs else ""
                            by_shard[shard][node_id] = {"desc": desc, "sig": sig}

        for shard, shard_entries in by_shard.items():
            shard_path = d / f"{shard}.json"
            existing = {}
            if shard_path.exists() and current_node_ids is None:
                try:
                    existing = json.loads(shard_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            existing.update(shard_entries)
            if existing:
                _atomic_write_json(shard_path, existing)
            else:
                try:
                    shard_path.unlink()
                except OSError:
                    pass

        if legacy.exists():
            try:
                legacy.unlink()
            except OSError:
                pass
    except OSError as e:
        logger.warning("Failed to save description cache: %s", e)


def _file_desc_cache_dir(root: Path) -> Path:
    d = root / ".indexer" / "cache" / "fdesc"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _fdesc_shard_key(file_path: str) -> str:
    return file_path[0].lower() if file_path else "0"


def load_cached_file_descriptions(root: Path) -> dict[str, dict]:
    d = _file_desc_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "file_descriptions.json"
    if legacy.exists() and not any(d.iterdir()):
        try:
            raw = json.loads(legacy.read_text())
            result = {}
            for k, v in raw.items():
                if isinstance(v, str):
                    result[k] = {"desc": v, "sig": ""}
                elif isinstance(v, dict):
                    result[k] = v
            return result
        except (json.JSONDecodeError, OSError):
            pass
    result = {}
    for shard_file in d.glob("*.json"):
        try:
            data = json.loads(shard_file.read_text())
            for k, v in data.items():
                if isinstance(v, str):
                    result[k] = {"desc": v, "sig": ""}
                elif isinstance(v, dict):
                    result[k] = v
        except (json.JSONDecodeError, OSError):
            pass
    return result


def save_cached_file_descriptions(root: Path, descriptions: dict[str, str], current_files: set[str] | None = None, sigs: dict[str, str] | None = None) -> None:
    d = _file_desc_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "file_descriptions.json"
    try:
        by_shard: dict[str, dict] = {}
        for file_path, desc in descriptions.items():
            shard = _fdesc_shard_key(file_path)
            sig = sigs.get(file_path, "") if sigs else ""
            by_shard.setdefault(shard, {})[file_path] = {"desc": desc, "sig": sig}

        if current_files is not None:
            for shard_file in d.glob("*.json"):
                try:
                    data = json.loads(shard_file.read_text())
                except (json.JSONDecodeError, OSError):
                    continue
                shard = shard_file.stem
                stale = [k for k in data if k not in current_files]
                if stale:
                    for k in stale:
                        del data[k]
                if stale or shard in by_shard:
                    by_shard[shard] = data
                    for file_path, desc in descriptions.items():
                        if _fdesc_shard_key(file_path) == shard:
                            sig = sigs.get(file_path, "") if sigs else ""
                            by_shard[shard][file_path] = {"desc": desc, "sig": sig}

        for shard, shard_entries in by_shard.items():
            shard_path = d / f"{shard}.json"
            existing = {}
            if shard_path.exists() and current_files is None:
                try:
                    existing = json.loads(shard_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            existing.update(shard_entries)
            if existing:
                _atomic_write_json(shard_path, existing)
            else:
                try:
                    shard_path.unlink()
                except OSError:
                    pass

        if legacy.exists():
            try:
                legacy.unlink()
            except OSError:
                pass
    except OSError as e:
        logger.warning("Failed to save file description cache: %s", e)


def cross_reference(all_nodes: list[ASTNode]) -> None:
    seen_ids: set[str] = set()
    unique_nodes: list[ASTNode] = []
    id_to_first: dict[str, ASTNode] = {}
    for node in all_nodes:
        if node.id not in seen_ids:
            seen_ids.add(node.id)
            unique_nodes.append(node)
            id_to_first[node.id] = node

    call_index: dict[str, list[str]] = {}
    file_call_index: dict[tuple[str, str], list[str]] = {}
    for node in unique_nodes:
        for callee_name in node.calls:
            call_index.setdefault(callee_name, []).append(node.id)
            file_call_index.setdefault((node.file, callee_name), []).append(node.id)
    for node in unique_nodes:
        bare_name = node.id.split("::")[-1]
        same_file_callers = file_call_index.get((node.file, bare_name), [])
        global_callers = call_index.get(bare_name, [])
        if same_file_callers:
            seen = set(same_file_callers)
            node.called_by = list(dict.fromkeys(same_file_callers + [c for c in global_callers if c not in seen]))
        else:
            node.called_by = list(dict.fromkeys(global_callers))

    for node in all_nodes:
        ref = id_to_first.get(node.id)
        if ref is not None and ref is not node:
            node.called_by = ref.called_by


def load_existing_nodes(root: Path, manifest: Manifest, cfg: Config) -> list[ASTNode]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _load_one(item):
        rel_path, entry = item
        abs_path = root / rel_path
        if not abs_path.exists():
            return []
        short_hash = entry.hash[7:7+16] if entry.hash and entry.hash.startswith("sha256:") else (entry.hash[:16] if entry.hash else compute_hash_short(abs_path))
        cached = load_cached_nodes(root, short_hash)
        return cached if cached is not None else []

    items = list(manifest.files.items())
    if len(items) < 50:
        existing_nodes = []
        for item in items:
            existing_nodes.extend(_load_one(item))
        return existing_nodes

    existing_nodes = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_load_one, item) for item in items]
        for future in as_completed(futures):
            try:
                existing_nodes.extend(future.result())
            except Exception:
                pass
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


def _collect_affected_files(candidates: set[str], all_nodes: list[ASTNode], existing_called_by: dict[str, list[str]]) -> set[str]:
    affected = set(candidates)
    for node in all_nodes:
        old = existing_called_by.get(node.id, [])
        new = node.called_by or []
        if old != new:
            affected.add(node.file)
    return affected


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
    all_files: list[str] | None = None,
    affected_files: set[str] | None = None,
) -> tuple[list[IndexEntry], dict[str, str]]:
    group_source = all_files if all_files is not None else candidates
    groups = precomputed_groups if precomputed_groups is not None else density_group(group_source, merge_threshold=cfg.merge_threshold)
    group_nodes: dict[str, list] = {}
    for node in all_nodes:
        group = groups.get(node.file, node.file)
        group_nodes.setdefault(group, []).append(node)

    write_groups: set[str] | None = None
    if affected_files is not None:
        write_groups = set()
        for f in affected_files:
            write_groups.add(groups.get(f, f))

    wiki_dir = root / cfg.wiki_dir
    index_entries = []

    for group_label, nodes in group_nodes.items():
        if write_groups is not None and group_label not in write_groups:
            continue
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


def _embedding_cache_dir(root: Path) -> Path:
    d = root / ".indexer" / "cache" / "emb"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _emb_shard_key(node_id: str) -> str:
    return node_id[0].lower() if node_id else "0"


def load_cached_embeddings(root: Path) -> dict[str, dict]:
    d = _embedding_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "embeddings.json"
    if legacy.exists() and not any(d.iterdir()):
        try:
            return json.loads(legacy.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    result = {}
    for shard_file in d.glob("*.json"):
        try:
            data = json.loads(shard_file.read_text())
            result.update(data)
        except (json.JSONDecodeError, OSError):
            pass
    return result


def save_cached_embeddings(root: Path, entries: dict[str, dict], current_node_ids: set[str] | None = None) -> None:
    d = _embedding_cache_dir(root)
    legacy = root / ".indexer" / "cache" / "embeddings.json"
    try:
        by_shard: dict[str, dict] = {}
        for node_id, entry in entries.items():
            shard = _emb_shard_key(node_id)
            by_shard.setdefault(shard, {})[node_id] = entry

        if current_node_ids is not None:
            for shard_file in d.glob("*.json"):
                try:
                    data = json.loads(shard_file.read_text())
                except (json.JSONDecodeError, OSError):
                    continue
                shard = shard_file.stem
                stale = [k for k in data if k not in current_node_ids]
                if stale:
                    for k in stale:
                        del data[k]
                if stale or shard in by_shard:
                    by_shard[shard] = data
                    for node_id, entry in entries.items():
                        if _emb_shard_key(node_id) == shard:
                            by_shard[shard][node_id] = entry

        for shard, shard_entries in by_shard.items():
            shard_path = d / f"{shard}.json"
            existing = {}
            if shard_path.exists() and current_node_ids is None:
                try:
                    existing = json.loads(shard_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            existing.update(shard_entries)
            if existing:
                _atomic_write_json(shard_path, existing)
            else:
                try:
                    shard_path.unlink()
                except OSError:
                    pass

        if legacy.exists():
            try:
                legacy.unlink()
            except OSError:
                pass
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
    existing_node_ids: set[str] | None = None,
) -> None:
    if removed_files is None:
        if is_git_repo(root):
            tracked = all_tracked_files(root)
        else:
            tracked = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)]
        removed_files = manifest.removed_files(root, tracked)
    if removed_files:
        vs_delete(removed_files, cfg.vector_store, root, branch=branch)

    if not all_nodes:
        return

    seen_ids: set[str] = set()
    deduped_nodes: list[ASTNode] = []
    for node in all_nodes:
        if node.id not in seen_ids:
            seen_ids.add(node.id)
            deduped_nodes.append(node)
    if len(deduped_nodes) < len(all_nodes):
        logger.warning("Deduplicated nodes: %d -> %d", len(all_nodes), len(deduped_nodes))
    all_nodes = deduped_nodes

    all_seen_ids = seen_ids | (existing_node_ids or set())

    cached_emb = load_cached_embeddings(root)
    hit_vectors: dict[str, list[float]] = {}
    miss_nodes: list[ASTNode] = []

    for node in all_nodes:
        sig = compute_embedding_sig(node, descriptions.get(node.id, ""))
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
                sig = compute_embedding_sig(node, descriptions.get(node.id, ""))
                new_cache_entries[node.id] = {"sig": sig, "vec": vec}
        save_cached_embeddings(root, new_cache_entries, current_node_ids=all_seen_ids)
        hit_vectors.update(new_vectors)
    else:
        logger.info("Embedding cache hit: %d/%d nodes, 0 API calls", len(hit_vectors), len(all_nodes))
        if cached_emb and set(cached_emb.keys()) - all_seen_ids:
            save_cached_embeddings(root, {}, current_node_ids=all_seen_ids)

    if len(hit_vectors) < len(all_nodes):
        logger.warning("Embedding incomplete: %d/%d vectors available", len(hit_vectors), len(all_nodes))

    vs_upsert(all_nodes, hit_vectors, descriptions, cfg.vector_store, root, dim=cfg.embedding.dimensions, branch=branch)
