# indexer/retrieval.py
from __future__ import annotations
import json
from pathlib import Path
from indexer.config import Config
from indexer.embedding import embed_query
from indexer.vector_store import search, get_by_ids


def search_symbols(
    query: str,
    cfg: Config,
    repo_root: Path,
    top_k: int = 10,
    expand_depth: int = 1,
    branch: str = "",
) -> list[dict]:
    top_k = min(top_k, 100)
    query_vector = embed_query(query, cfg.embedding)
    where_clause = {"branch": branch} if branch else None
    hits = search(query_vector, cfg.vector_store, repo_root, top_k=top_k, where=where_clause)

    for h in hits:
        if "document" in h and h["document"]:
            h["document"] = h["document"][:2000]

    if expand_depth > 0:
        hits = _expand_with_call_graph(hits, cfg, repo_root, expand_depth)
        for h in hits:
            if "document" in h and h["document"]:
                h["document"] = h["document"][:2000]

    return hits


def trace_call(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    direction: str = "down",
    max_depth: int = 3,
) -> list[dict]:
    max_depth = min(max_depth, 8)
    seed = get_by_ids([symbol_id], cfg.vector_store, repo_root)
    if not seed:
        return []

    result_nodes = [seed[0]]
    visited = {symbol_id}

    current_ids = set()
    if direction == "down":
        calls_raw = seed[0].get("metadata", {}).get("calls", "")
        current_ids = set(_parse_json_list(calls_raw))
    elif direction == "up":
        called_by_raw = seed[0].get("metadata", {}).get("called_by", "")
        current_ids = set(_parse_json_list(called_by_raw))

    for _ in range(max_depth):
        next_ids = set()
        if not current_ids:
            break

        batch = get_by_ids(list(current_ids), cfg.vector_store, repo_root)
        for node in batch:
            nid = node["id"]
            if nid in visited:
                continue
            visited.add(nid)
            result_nodes.append(node)

            meta = node.get("metadata", {})
            if direction == "down":
                next_ids.update(_parse_json_list(meta.get("calls", "")))
            elif direction == "up":
                next_ids.update(_parse_json_list(meta.get("called_by", "")))

        current_ids = next_ids - visited

    return result_nodes


def get_source_context(
    file_path: str,
    line_start: int,
    line_end: int,
    repo_root: Path,
    padding: int = 5,
) -> str:
    padding = min(padding, 50)
    abs_path = (repo_root / file_path).resolve()
    root_resolved = repo_root.resolve()

    if not abs_path.is_relative_to(root_resolved):
        return "Access denied: path outside repo root"

    if not abs_path.exists():
        return f"File not found: {file_path}"

    try:
        lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return f"Cannot read file: {file_path}"

    start = max(1, line_start - padding) - 1
    end = min(len(lines), line_end + padding)
    # Anti-scraping: hard cap total returned lines
    MAX_LINES = 500
    if end - start > MAX_LINES:
        end = start + MAX_LINES

    selected = lines[start:end]
    numbered = [f"{i+1:>4} | {line}" for i, line in zip(range(start, end), selected)]
    return "\n".join(numbered)


def _expand_with_call_graph(
    hits: list[dict],
    cfg: Config,
    repo_root: Path,
    depth: int = 1,
) -> list[dict]:
    expanded = list(hits)
    visited = {h["id"] for h in hits}
    frontier = hits

    for _ in range(depth):
        next_frontier = []
        for hit in frontier:
            meta = hit.get("metadata", {})
            related_ids = set()
            related_ids.update(_parse_json_list(meta.get("calls", "")))
            related_ids.update(_parse_json_list(meta.get("called_by", "")))
            related_ids -= visited

            if related_ids:
                batch = get_by_ids(list(related_ids), cfg.vector_store, repo_root)
                for node in batch:
                    if node["id"] not in visited:
                        visited.add(node["id"])
                        expanded.append(node)
                        next_frontier.append(node)
        frontier = next_frontier
        if not frontier:
            break

    return expanded


def _parse_json_list(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
