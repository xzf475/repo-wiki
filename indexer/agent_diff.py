from __future__ import annotations

import hashlib
from pathlib import Path

from indexer.config import Config
from indexer.repository_service import RepositoryService, default_branch
import indexer.retrieval as _retrieval
from indexer.retrieval import (
    _git_diff,
    _has_code_changes,
    _has_config_changes,
    _is_test_path,
    _limit_list,
    _node_edges,
    _normalize_source_signature,
    _parse_diff_changed_files,
    _parse_diff_new_ranges,
    _stable_id_moves,
    _symbols_for_changed_files,
)

def post_edit_verify(
    cfg: Config,
    repo_root: Path,
    diff: str = "",
    changed_files: list[str] | None = None,
) -> dict:
    if not diff:
        diff = _git_diff(repo_root)
    parsed_files = _parse_diff_changed_files(diff)
    files = list(dict.fromkeys((changed_files or []) + parsed_files))
    changed_ranges = _parse_diff_new_ranges(diff)
    changed_symbols = _symbols_for_changed_files(cfg, repo_root, files, changed_ranges)

    candidate_tests = []
    for item in changed_symbols:
        candidate_tests.extend(_retrieval.find_tests_for_symbol(item["id"], cfg, repo_root, max_results=5))
    seen_tests = {}
    for test in candidate_tests:
        key = test.get("file")
        if key and key not in seen_tests:
            seen_tests[key] = test
    tests = list(seen_tests.values())

    commands = _retrieval.recommend_test_commands(repo_root, tests)
    if not commands and _has_code_changes(files):
        commands = _retrieval.recommend_test_commands(repo_root, [])
    index_status = _retrieval.get_index_status(repo_root)
    risks = []
    if any(item.get("entry_point") for item in changed_symbols):
        risks.append("Changed entry point; verify request/command flow")
    if _has_config_changes(files):
        risks.append("Changed config or dependency file; consider full test/build")
    if _has_code_changes(files) and not tests:
        risks.append("No candidate tests found for changed symbols")
    if index_status.get("is_stale"):
        risks.append("Index is stale after edits")

    checklist = [
        "Review changed symbols and affected entry points",
        "Run recommended verification commands",
    ]
    if risks:
        checklist.append("Review risk points before commit")
    if index_status.get("is_stale") or files:
        checklist.append("Run repo-wiki run after verification")

    return {
        "changed_files": files,
        "changed_symbols": changed_symbols,
        "candidate_tests": tests,
        "verify_commands": commands,
        "risk_points": risks,
        "needs_sync": bool(files) or bool(index_status.get("is_stale")),
        "index_status": index_status,
        "checklist": checklist,
    }


def stable_symbol_id(symbol_id: str, symbol_type: str = "", file_path: str = "", source: str = "") -> str:
    logical = symbol_id.rsplit("::", 1)[-1].lower()
    payload = "|".join([logical, symbol_type.lower(), Path(file_path).suffix.lower(), _normalize_source_signature(source)])
    return "sym:" + hashlib.sha1(payload.encode("utf-8", errors="replace")).hexdigest()[:16]


def change_set(
    goal: str,
    cfg: Config,
    repo_root: Path,
    symbol_id: str = "",
    diff: str = "",
    changed_files: list[str] | None = None,
    max_results: int = 50,
    include_details: bool = True,
) -> dict:
    max_results = max(1, min(max_results, 500))
    post = _retrieval.post_edit_verify(cfg, repo_root, diff=diff, changed_files=changed_files)
    target_ids = [symbol_id] if symbol_id else [item["id"] for item in post.get("changed_symbols", []) if item.get("id")]
    must_files = list(post.get("changed_files", []))
    related_symbols = []
    tests = list(post.get("candidate_tests", []))
    risks = list(post.get("risk_points", []))
    for target in target_ids:
        impact = _retrieval.impact_analysis(target, cfg, repo_root)
        symbol = impact.get("symbol") or {}
        if symbol.get("metadata", {}).get("file"):
            must_files.append(symbol["metadata"]["file"])
        for node in impact.get("direct_callers", []) + impact.get("direct_callees", []):
            if node.get("id"):
                related_symbols.append(node["id"])
            if node.get("metadata", {}).get("file"):
                must_files.append(node["metadata"]["file"])
        for path in impact.get("affected_files", []):
            must_files.append(path)
        tests.extend(impact.get("candidate_tests", []))
        risks.extend(impact.get("risk_points", []))

    test_by_file = {item.get("file"): item for item in tests if item.get("file")}
    all_files = list(dict.fromkeys(must_files))
    all_related = list(dict.fromkeys(related_symbols))
    all_tests = list(test_by_file.values())
    all_commands = list(dict.fromkeys(post.get("verify_commands", []) + _retrieval.recommend_test_commands(repo_root, all_tests)))
    all_risks = list(dict.fromkeys(risks))
    result = {
        "goal": goal,
        "summary": {
            "changed_file_count": len(post.get("changed_files", [])),
            "target_symbol_count": len(target_ids),
            "must_change_file_count": len(all_files),
            "related_symbol_count": len(all_related),
            "candidate_test_count": len(all_tests),
            "risk_count": len(all_risks),
        },
        "target_symbols": _limit_list(target_ids, max_results),
        "must_change_files": _limit_list(all_files, max_results),
        "related_symbols": _limit_list(all_related, max_results),
        "candidate_tests": _limit_list(all_tests, max_results),
        "verify_commands": _limit_list(all_commands, max_results),
        "risk_points": _limit_list(all_risks, max_results),
        "index_status": _retrieval.get_index_status(repo_root),
    }
    if not include_details:
        result["details_omitted"] = True
        result["candidate_tests"] = []
    return result


def coverage_map(cfg: Config, repo_root: Path, symbol_id: str = "", max_results: int = 100) -> dict:
    max_results = max(1, min(max_results, 500))
    service = RepositoryService(
        repo_root.name,
        repo_root,
        default_branch(repo_root),
        config=cfg,
    )
    source_ids = [symbol_id] if symbol_id else [
        record.component_id
        for record in service.index.symbols(service.scope)
        if not _is_test_path(record.file)
    ]
    tests_by_symbol = {}
    for sid in source_ids:
        tests_by_symbol[sid] = _retrieval.find_tests_for_symbol(sid, cfg, repo_root, max_results=20)
    if symbol_id:
        tests = tests_by_symbol.get(symbol_id, [])
        return {"symbol_id": symbol_id, "covered": bool(tests), "tests": _limit_list(tests, max_results), "index_status": _retrieval.get_index_status(repo_root)}
    symbols = [
            {"symbol_id": sid, "covered": bool(tests), "tests": tests}
            for sid, tests in tests_by_symbol.items()
        ]
    return {
        "symbols": _limit_list(symbols, max_results),
        "total": len(tests_by_symbol),
        "index_status": _retrieval.get_index_status(repo_root),
    }


def index_diff_report(
    cfg: Config,
    repo_root: Path,
    before_nodes: list[dict] | None = None,
    after_nodes: list[dict] | None = None,
) -> dict:
    before_nodes = before_nodes or []
    after_nodes = after_nodes or []
    before = {n["id"]: n for n in before_nodes if n.get("id")}
    after = {n["id"]: n for n in after_nodes if n.get("id")}
    before_ids = set(before)
    after_ids = set(after)
    added = sorted(after_ids - before_ids)
    removed = sorted(before_ids - after_ids)
    renamed_or_moved = _stable_id_moves(before, after, removed, added)
    moved_before = {item["before"] for item in renamed_or_moved}
    moved_after = {item["after"] for item in renamed_or_moved}
    added = [sid for sid in added if sid not in moved_after]
    removed = [sid for sid in removed if sid not in moved_before]
    common = before_ids & after_ids
    changed = sorted([
        sid for sid in common
        if before[sid].get("metadata", {}) != after[sid].get("metadata", {}) or before[sid].get("document", "") != after[sid].get("document", "")
    ])
    before_entry = {sid for sid, node in before.items() if node.get("metadata", {}).get("entry_point")}
    after_entry = {sid for sid, node in after.items() if node.get("metadata", {}).get("entry_point")}
    before_edges = _node_edges(before_nodes)
    after_edges = _node_edges(after_nodes)
    return {
        "added_symbols": added,
        "removed_symbols": removed,
        "renamed_or_moved_symbols": renamed_or_moved,
        "changed_symbols": changed,
        "entry_point_changes": {
            "added": sorted(after_entry - before_entry),
            "removed": sorted(before_entry - after_entry),
        },
        "call_graph_changes": {
            "added_edges": sorted([list(edge) for edge in after_edges - before_edges]),
            "removed_edges": sorted([list(edge) for edge in before_edges - after_edges]),
        },
        "index_status": _retrieval.get_index_status(repo_root),
    }

__all__ = ['post_edit_verify', 'stable_symbol_id', 'change_set', 'coverage_map', 'index_diff_report']
