from __future__ import annotations

from pathlib import Path

from indexer.config import Config
import indexer.retrieval as _retrieval
from indexer.retrieval import (
    _extract_error_frames,
    _extract_error_terms,
    _extract_http_paths,
    _freshness_risks,
    _infer_entry_point_kind_from_hit,
    _looks_like_entry_point,
    _natural_language_alias_score,
    _parse_json_list,
)

def resolve_symbol(
    query: str,
    cfg: Config,
    repo_root: Path,
    file_hint: str = "",
    type_hint: str = "",
    top_k: int = 10,
) -> dict:
    hits = _retrieval.search_symbols(query, cfg, repo_root, top_k=top_k, expand_depth=0, explain=True)
    if not hits:
        return {"status": "not_found", "query": query, "candidates": []}

    query_norm = query.lower().replace("::", ".")
    file_hint_norm = file_hint.lower()
    type_hint_norm = type_hint.lower()
    ranked = []
    for hit in hits:
        meta = hit.get("metadata", {})
        symbol_name = hit["id"].rsplit("::", 1)[-1].lower()
        file_path = str(meta.get("file", "")).lower()
        typ = str(meta.get("type", "")).lower()
        reasons = list(hit.get("match_reasons", []))
        alias_score = _natural_language_alias_score(query, hit)
        score = 0
        if query_norm and query_norm in hit["id"].lower().replace("::", "."):
            score += 5
            reasons.append("symbol id match")
        if symbol_name and query_norm.endswith(symbol_name):
            score += 4
            reasons.append("symbol name match")
        if file_hint_norm and file_hint_norm in file_path:
            score += 6
            reasons.append("file hint match")
        if type_hint_norm and type_hint_norm == typ:
            score += 2
            reasons.append("type hint match")
        if alias_score:
            score += alias_score
            reasons.append("natural language alias match")
        try:
            score += max(0, 2 - float(hit.get("distance", 1.0)))
        except (TypeError, ValueError):
            pass
        ranked_hit = dict(hit)
        ranked_hit["resolve_score"] = score
        ranked_hit["match_reasons"] = list(dict.fromkeys(reasons))
        ranked.append(ranked_hit)

    ranked.sort(key=lambda h: (-h["resolve_score"], h["id"]))
    status = "resolved" if len(ranked) == 1 or ranked[0]["resolve_score"] > ranked[1]["resolve_score"] else "ambiguous"
    return {"status": status, "query": query, "symbol": ranked[0] if status == "resolved" else None, "candidates": ranked}


def impact_analysis(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    max_depth: int = 2,
) -> dict:
    max_depth = max(1, min(max_depth, 5))
    seed = _retrieval.get_by_ids([symbol_id], cfg.vector_store, repo_root)
    if not seed:
        return {
            "symbol": None,
            "error": f"symbol '{symbol_id}' not found",
            "index_status": _retrieval.get_index_status(repo_root),
        }

    symbol = seed[0]
    meta = symbol.get("metadata", {})
    caller_ids = _parse_json_list(meta.get("called_by", ""))
    callee_ids = _parse_json_list(meta.get("calls", ""))
    direct_callers = _retrieval.get_by_ids(caller_ids, cfg.vector_store, repo_root) if caller_ids else []
    direct_callees = _retrieval.get_by_ids(callee_ids, cfg.vector_store, repo_root) if callee_ids else []
    upstream = _retrieval.trace_call(symbol_id, cfg, repo_root, direction="up", max_depth=max_depth)
    downstream = _retrieval.trace_call(symbol_id, cfg, repo_root, direction="down", max_depth=max_depth)

    direct_ids = {symbol_id, *caller_ids, *callee_ids}
    indirect_callers = [n for n in upstream if n.get("id") not in direct_ids]
    indirect_callees = [n for n in downstream if n.get("id") not in direct_ids]
    all_nodes = [symbol] + direct_callers + direct_callees + indirect_callers + indirect_callees
    affected_files = sorted({
        str(n.get("metadata", {}).get("file", ""))
        for n in all_nodes
        if n.get("metadata", {}).get("file")
    })
    tests = _retrieval.find_tests_for_symbol(symbol_id, cfg, repo_root, max_results=10)
    affected_files.extend(t["file"] for t in tests if t.get("file") and t["file"] not in affected_files)

    entry_points = [
        n for n in direct_callers + indirect_callers
        if _looks_like_entry_point(n)
    ]
    risk_points = []
    if not direct_callers:
        risk_points.append("No direct callers found in static call graph")
    if not tests:
        risk_points.append("No candidate tests found")
    index_status = _retrieval.get_index_status(repo_root)
    if index_status.get("is_stale"):
        risk_points.append("Index is stale; impact may be incomplete")

    return {
        "symbol": symbol,
        "direct_callers": direct_callers,
        "direct_callees": direct_callees,
        "indirect_callers": indirect_callers,
        "indirect_callees": indirect_callees,
        "entry_points": entry_points,
        "candidate_tests": tests,
        "affected_files": affected_files,
        "risk_points": risk_points,
        "index_status": index_status,
    }


def change_plan(goal: str, symbol_id: str, cfg: Config, repo_root: Path) -> dict:
    check = _retrieval.pre_edit_check(symbol_id, cfg, repo_root)
    impact = impact_analysis(symbol_id, cfg, repo_root)
    symbol = impact.get("symbol") or {}
    meta = symbol.get("metadata", {})
    source_file = str(meta.get("file", symbol_id.split("::", 1)[0]))
    line_start = int(meta.get("line_start", 1) or 1)
    line_end = int(meta.get("line_end", line_start) or line_start)
    affected_files = list(dict.fromkeys(impact.get("affected_files", []) or [source_file]))
    read_files = [
        {"file": source_file, "line_start": line_start, "line_end": line_end, "reason": "primary edit target"}
    ]
    for file_path in affected_files:
        if file_path != source_file:
            read_files.append({"file": file_path, "reason": "related impact or verification target"})

    index_status = check.get("index_status", _retrieval.get_index_status(repo_root))
    risks = list(dict.fromkeys((impact.get("risk_points") or []) + _freshness_risks(index_status)))
    if check.get("dirty_files"):
        risks.append("Workspace has dirty files; avoid overwriting unrelated changes")

    return {
        "goal": goal,
        "target_symbol_id": symbol_id,
        "index_status": index_status,
        "read_these_files": read_files,
        "edit_targets": [{
            "file": source_file,
            "symbol_id": symbol_id,
            "line_start": line_start,
            "line_end": line_end,
        }],
        "verify_commands": check.get("recommended_commands", []),
        "candidate_tests": check.get("candidate_tests", []),
        "risk_points": list(dict.fromkeys(risks)),
        "steps": [
            "Confirm index freshness and dirty workspace state",
            "Read the primary symbol context and direct call sites",
            "Apply the smallest scoped code change",
            "Run the recommended verification commands",
        ],
    }


def list_entry_points(
    cfg: Config,
    repo_root: Path,
    kind: str = "",
    max_results: int = 50,
) -> dict:
    from indexer.manifest import load_manifest

    max_results = max(1, min(max_results, 200))
    manifest = load_manifest(repo_root)
    ids = []
    for entry in manifest.files.values():
        ids.extend(entry.component_ids)
    nodes = _retrieval.get_by_ids(ids, cfg.vector_store, repo_root) if ids else []

    results = []
    for node in nodes:
        meta = node.get("metadata", {})
        entry_kind = str(meta.get("entry_point_kind") or "")
        entry = bool(meta.get("entry_point")) or bool(entry_kind) or _looks_like_entry_point(node)
        if not entry:
            continue
        if not entry_kind:
            entry_kind = _infer_entry_point_kind_from_hit(node)
        if kind and entry_kind != kind:
            continue
        results.append({
            "id": node.get("id"),
            "kind": entry_kind or "unknown",
            "file": meta.get("file"),
            "line_start": meta.get("line_start"),
            "line_end": meta.get("line_end"),
            "document": node.get("document", ""),
        })

    results.sort(key=lambda item: (item.get("kind", ""), item.get("file") or "", item.get("id") or ""))
    results = results[:max_results]
    return {"results": results, "total": len(results), "index_status": _retrieval.get_index_status(repo_root)}


def locate_from_error(
    error_text: str,
    cfg: Config,
    repo_root: Path,
    top_k: int = 10,
) -> dict:
    from indexer.manifest import load_manifest

    top_k = max(1, min(top_k, 50))
    frames = _extract_error_frames(error_text)
    http_paths = _extract_http_paths(error_text)
    terms = _extract_error_terms(error_text)
    manifest = load_manifest(repo_root)
    ids = []
    for entry in manifest.files.values():
        ids.extend(entry.component_ids)
    indexed_nodes = _retrieval.get_by_ids(ids, cfg.vector_store, repo_root) if ids else []

    scored = []
    for node in indexed_nodes:
        score = 0
        reasons = []
        meta = node.get("metadata", {})
        file_path = str(meta.get("file", ""))
        line_start = int(meta.get("line_start", 0) or 0)
        line_end = int(meta.get("line_end", 0) or 0)
        hay = " ".join([node.get("id", ""), node.get("document", ""), file_path]).lower()

        for frame in frames:
            if frame["file"].endswith(file_path) or file_path.endswith(frame["file"]):
                score += 6
                reasons.append("stack frame file match")
                if line_start and line_end and line_start <= frame["line"] <= line_end:
                    score += 8
                    reasons.append("stack frame line inside symbol")
        for path in http_paths:
            if path.lower() in hay:
                score += 7
                reasons.append("http path match")
        for term in terms:
            if term in hay:
                score += 1
        if meta.get("entry_point") and http_paths:
            score += 2
            reasons.append("entry point candidate")

        if score:
            hit = dict(node)
            hit["locate_score"] = score
            hit["reasons"] = list(dict.fromkeys(reasons))
            scored.append(hit)

    if len(scored) < top_k and terms:
        query = " ".join(terms[:12])
        for hit in _retrieval.search_symbols(query, cfg, repo_root, top_k=top_k, expand_depth=0, explain=True):
            if any(existing.get("id") == hit.get("id") for existing in scored):
                continue
            hit = dict(hit)
            hit["locate_score"] = max(1, int(10 - float(hit.get("distance", 1.0))))
            hit["reasons"] = list(dict.fromkeys(["semantic error text match"] + hit.get("match_reasons", [])))
            scored.append(hit)

    scored.sort(key=lambda item: (-item.get("locate_score", 0), item.get("id", "")))
    candidates = scored[:top_k]
    return {
        "frames": frames,
        "http_paths": http_paths,
        "terms": terms[:20],
        "candidates": candidates,
        "total": len(candidates),
        "index_status": _retrieval.get_index_status(repo_root),
    }

__all__ = ['resolve_symbol', 'impact_analysis', 'change_plan', 'list_entry_points', 'locate_from_error']
