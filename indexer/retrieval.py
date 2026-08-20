# indexer/retrieval.py
from __future__ import annotations
import json
import os
import re
import subprocess
from pathlib import Path
from indexer.config import Config
from indexer.git_snapshot import WORKTREE_REVISION
from indexer.repository_service import RepositoryService, default_branch

MAX_DOC_LEN = 2000


def truncate_documents(hits: list[dict], max_len: int = MAX_DOC_LEN) -> None:
    for h in hits:
        if "document" in h and h["document"] and len(h["document"]) > max_len:
            h["document"] = h["document"][:max_len]


def search_symbols(
    query: str,
    cfg: Config,
    repo_root: Path,
    top_k: int = 10,
    expand_depth: int = 1,
    branch: str = "",
    explain: bool = False,
) -> list[dict]:
    response = search_code(
        query,
        cfg,
        repo_root,
        top_k=top_k,
        expand_depth=expand_depth,
        branch=branch,
        explain=explain,
    )
    matches = response["matches"]
    truncate_documents(matches)
    return matches


def search_code(
    query: str,
    cfg: Config,
    repo_root: Path,
    top_k: int = 10,
    expand_depth: int = 1,
    branch: str = "",
    retrieval: str = "preferred",
    explain: bool = True,
) -> dict:
    selected_branch = branch or default_branch(repo_root)
    service = RepositoryService(
        repo_root.name,
        repo_root,
        selected_branch,
        config=cfg,
    )
    response = service.search(
        query,
        limit=top_k,
        related_limit=top_k if expand_depth else 0,
        retrieval=retrieval,
    )
    if expand_depth > 1:
        seen = {hit["id"] for hit in response["matches"]}
        related = list(response["related"])
        seen.update(hit["id"] for hit in related)
        for match in response["matches"]:
            for item in service.trace(
                match["id"],
                direction="down",
                max_depth=expand_depth,
            )[1:]:
                if item["id"] in seen:
                    continue
                seen.add(item["id"])
                item["relation"] = "call"
                related.append(item)
                if len(related) >= top_k:
                    break
        response["related"] = related[:top_k]
    return response


def get_by_ids(
    component_ids: list[str] | tuple[str, ...],
    repo_root: Path,
    *,
    branch: str = "",
) -> list[dict]:
    """Read structural records from the current generation."""
    selected_branch = branch or default_branch(repo_root)
    return RepositoryService(
        repo_root.name,
        repo_root,
        selected_branch,
    ).lookup(component_ids)


def resolve_symbol(*args, **kwargs):
    from indexer.agent_context import resolve_symbol as _impl
    return _impl(*args, **kwargs)

def impact_analysis(*args, **kwargs):
    from indexer.agent_context import impact_analysis as _impl
    return _impl(*args, **kwargs)

def change_plan(*args, **kwargs):
    from indexer.agent_context import change_plan as _impl
    return _impl(*args, **kwargs)

def diagnose_index(*args, **kwargs):
    from indexer.agent_diagnostics import diagnose_index as _impl
    return _impl(*args, **kwargs)

def agent_protocol_bundle(
    goal: str,
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    protocol: str = "codex",
) -> dict:
    plan = change_plan(goal, symbol_id, cfg, repo_root)
    read_targets = []
    for item in plan.get("read_these_files", []):
        file_path = item.get("file", "")
        if item.get("line_start") and item.get("line_end"):
            read_targets.append(f"{file_path}:{item['line_start']}-{item['line_end']}")
        elif file_path:
            read_targets.append(file_path)
    return {
        "protocol": protocol,
        "goal": goal,
        "target_symbol_id": symbol_id,
        "index_freshness": plan.get("index_status", {}),
        "read_these_files": read_targets,
        "edit_targets": [
            {
                "file": item.get("file"),
                "symbol_id": item.get("symbol_id"),
                "lines": f"{item.get('line_start')}-{item.get('line_end')}",
            }
            for item in plan.get("edit_targets", [])
        ],
        "verify_commands": plan.get("verify_commands", []),
        "warnings": plan.get("risk_points", []),
    }


def list_entry_points(*args, **kwargs):
    from indexer.agent_context import list_entry_points as _impl
    return _impl(*args, **kwargs)

def locate_from_error(*args, **kwargs):
    from indexer.agent_context import locate_from_error as _impl
    return _impl(*args, **kwargs)

def post_edit_verify(*args, **kwargs):
    from indexer.agent_diff import post_edit_verify as _impl
    return _impl(*args, **kwargs)

def stable_symbol_id(*args, **kwargs):
    from indexer.agent_diff import stable_symbol_id as _impl
    return _impl(*args, **kwargs)

def change_set(*args, **kwargs):
    from indexer.agent_diff import change_set as _impl
    return _impl(*args, **kwargs)

def coverage_map(*args, **kwargs):
    from indexer.agent_diff import coverage_map as _impl
    return _impl(*args, **kwargs)

def index_diff_report(*args, **kwargs):
    from indexer.agent_diff import index_diff_report as _impl
    return _impl(*args, **kwargs)

def cross_repo_graph(*args, **kwargs):
    from indexer.agent_graph import cross_repo_graph as _impl
    return _impl(*args, **kwargs)

def agent_capabilities_manifest() -> dict:
    from indexer.agent_contracts import agent_capabilities_manifest as _manifest
    return _manifest()


def trace_call(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    direction: str = "down",
    max_depth: int = 3,
) -> list[dict]:
    selected_branch = default_branch(repo_root)
    return RepositoryService(
        repo_root.name,
        repo_root,
        selected_branch,
        config=cfg,
    ).trace(
        symbol_id,
        direction=direction,
        max_depth=min(max_depth, 8),
    )


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


def get_index_status(repo_root: Path) -> dict:
    branch = default_branch(repo_root)
    return RepositoryService(repo_root.name, repo_root, branch).inspect(
        revision=WORKTREE_REVISION,
    )


def find_tests_for_symbol(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    max_results: int = 10,
) -> list[dict]:
    max_results = max(1, min(max_results, 50))
    seed = get_by_ids([symbol_id], repo_root)
    seed_meta = seed[0].get("metadata", {}) if seed else {}
    source_file = str(seed_meta.get("file") or symbol_id.split("::", 1)[0])
    symbol_name = symbol_id.rsplit("::", 1)[-1].split(".")[-1]
    source_stem = Path(source_file).stem

    service = RepositoryService(
        repo_root.name,
        repo_root,
        default_branch(repo_root),
        config=cfg,
    )
    indexed_files = service.index.files(service.scope)
    symbols_by_file: dict[str, list[str]] = {}
    for record in service.index.symbols(service.scope):
        symbols_by_file.setdefault(record.file, []).append(record.component_id)
    matches = []
    for rel_path in indexed_files:
        path = Path(rel_path)
        parts = set(path.parts)
        is_test = (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or "tests" in parts
            or "__tests__" in parts
            or path.suffix.lower() in {".spec.js", ".test.js", ".spec.ts", ".test.ts", ".spec.tsx", ".test.tsx"}
        )
        if not is_test:
            continue

        abs_path = repo_root / rel_path
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""

        reasons = []
        score = 0
        if symbol_name and symbol_name in text:
            score += 4
            reasons.append("symbol name match")
        if source_stem and source_stem in text:
            score += 2
            reasons.append("source module match")
        if source_file and source_file in text:
            score += 3
            reasons.append("source path match")
        component_ids = symbols_by_file.get(rel_path, [])
        if any(symbol_name and symbol_name in cid for cid in component_ids):
            score += 2
            reasons.append("test symbol name match")
        if source_stem and source_stem in path.name:
            score += 1
            reasons.append("test filename match")

        if score:
            matches.append({
                "file": rel_path,
                "score": score,
                "reasons": reasons,
                "component_ids": component_ids,
            })

    matches.sort(key=lambda item: (-item["score"], item["file"]))
    return matches[:max_results]


def get_edit_context(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    padding: int = 8,
    max_related: int = 20,
) -> dict:
    padding = max(0, min(padding, 50))
    max_related = max(1, min(max_related, 100))
    seed = get_by_ids([symbol_id], repo_root)
    if not seed:
        return {
            "symbol": None,
            "error": f"symbol '{symbol_id}' not found",
            "index_status": get_index_status(repo_root),
        }

    symbol = seed[0]
    meta = symbol.get("metadata", {})
    file_path = str(meta.get("file", ""))
    line_start = int(meta.get("line_start", 1) or 1)
    line_end = int(meta.get("line_end", line_start) or line_start)
    source = get_source_context(file_path, line_start, line_end, repo_root, padding=padding)

    call_ids = _parse_json_list(meta.get("calls", ""))
    caller_ids = _parse_json_list(meta.get("called_by", ""))
    callees = get_by_ids(call_ids[:max_related], repo_root) if call_ids else []
    callers = get_by_ids(caller_ids[:max_related], repo_root) if caller_ids else []

    service = RepositoryService(
        repo_root.name,
        repo_root,
        default_branch(repo_root),
        config=cfg,
    )
    sibling_ids = [
        record.component_id
        for record in service.index.symbols(service.scope, paths=(file_path,))
        if record.component_id != symbol_id
    ]
    siblings = get_by_ids(sibling_ids[:max_related], repo_root) if sibling_ids else []

    return {
        "symbol": symbol,
        "source": source,
        "imports": _parse_json_list(meta.get("imports", "")),
        "callers": callers,
        "callees": callees,
        "siblings": siblings,
        "candidate_tests": find_tests_for_symbol(symbol_id, cfg, repo_root, max_results=10),
        "index_status": get_index_status(repo_root),
    }


def pre_edit_check(symbol_id: str, cfg: Config, repo_root: Path) -> dict:
    context = get_edit_context(symbol_id, cfg, repo_root)
    candidate_tests = context.get("candidate_tests", [])
    return {
        "symbol_id": symbol_id,
        "index_status": context.get("index_status", get_index_status(repo_root)),
        "dirty_files": _git_dirty_files(repo_root),
        "candidate_tests": candidate_tests,
        "recommended_commands": recommend_test_commands(repo_root, candidate_tests),
        "callers": context.get("callers", []),
        "callees": context.get("callees", []),
    }


def recommend_test_commands(repo_root: Path, candidate_tests: list[dict] | None = None) -> list[str]:
    candidate_tests = candidate_tests or []
    test_files = [m["file"] for m in candidate_tests if m.get("file")]
    commands = []
    if (repo_root / "pytest.ini").exists() or (repo_root / "pyproject.toml").exists():
        if test_files:
            commands.extend(f"python3 -m pytest {path}" for path in test_files[:5])
        else:
            commands.append("python3 -m pytest")
    if (repo_root / "package.json").exists():
        commands.append("npm test")
    if (repo_root / "go.mod").exists():
        commands.append("go test ./...")
    if (repo_root / "Cargo.toml").exists():
        commands.append("cargo test")
    return list(dict.fromkeys(commands))


def _git_dirty_files(repo_root: Path) -> list[str]:
    if not (repo_root / ".git").exists():
        return []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    dirty = []
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            dirty.append(line[3:].strip())
    return dirty


def _expand_with_call_graph(
    hits: list[dict],
    cfg: Config,
    repo_root: Path,
    depth: int = 1,
    max_expanded: int = 50,
    branch: str = "",
) -> list[dict]:
    expanded = list(hits)
    visited = {h["id"] for h in hits}
    frontier = hits

    for _ in range(depth):
        next_frontier = []
        for hit in frontier:
            if len(expanded) >= max_expanded:
                return expanded
            meta = hit.get("metadata", {})
            related_ids = set()
            related_ids.update(_parse_json_list(meta.get("calls", "")))
            related_ids.update(_parse_json_list(meta.get("called_by", "")))
            related_ids -= visited

            if related_ids:
                batch = get_by_ids(list(related_ids), repo_root, branch=branch)
                for node in batch:
                    if len(expanded) >= max_expanded:
                        return expanded
                    if node["id"] not in visited:
                        visited.add(node["id"])
                        expanded.append(node)
                        next_frontier.append(node)
        frontier = next_frontier
        if not frontier:
            break

    return expanded


def _natural_language_alias_score(query: str, hit: dict) -> int:
    query_terms = {t for t in query.lower().replace("_", " ").replace("-", " ").split() if len(t) >= 2}
    if not query_terms:
        return 0
    meta = hit.get("metadata", {})
    hay = " ".join([
        hit.get("id", ""),
        hit.get("document", ""),
        str(meta.get("file", "")),
        str(meta.get("type", "")),
    ]).lower().replace("_", " ").replace("-", " ")
    aliases = {
        "login": {"login", "signin", "sign in", "auth", "authenticate", "/login"},
        "endpoint": {"endpoint", "route", "handler", "api", "post", "get", "put", "delete"},
        "index": {"index", "reindex", "rebuild", "sync"},
        "update": {"update", "refresh", "sync", "reindex", "rebuild"},
        "button": {"button", "click", "handler", "onclick", "submit"},
        "permission": {"permission", "role", "authz", "authorize", "access"},
        "auth": {"auth", "authenticate", "token", "jwt", "login"},
    }
    score = 0
    for term in query_terms:
        candidates = aliases.get(term, {term})
        if any(candidate in hay for candidate in candidates):
            score += 2
    return score


def _looks_like_entry_point(node: dict) -> bool:
    meta = node.get("metadata", {})
    hay = " ".join([
        node.get("id", ""),
        node.get("document", ""),
        str(meta.get("file", "")),
        str(meta.get("type", "")),
    ]).lower()
    markers = ["endpoint", "route", "handler", "controller", "cli", "command", "post /", "get /", "put /", "delete /"]
    return any(marker in hay for marker in markers)


def _freshness_risks(index_status: dict) -> list[str]:
    if not index_status.get("is_stale"):
        return []
    reasons = ", ".join(index_status.get("reasons", [])) or "unknown reason"
    return [f"Index is stale: {reasons}"]


def _infer_entry_point_kind_from_hit(hit: dict) -> str:
    meta = hit.get("metadata", {})
    hay = " ".join([
        hit.get("id", ""),
        hit.get("document", ""),
        str(meta.get("file", "")),
    ]).lower()
    if re.search(r"\b(get|post|put|patch|delete)\s+/", hay) or any(token in hay for token in ("endpoint", "route", "controller")):
        return "api"
    if any(token in hay for token in ("command", "cli")):
        return "cli"
    if any(token in hay for token in ("handler", "onclick", "on_click", "event")):
        return "event"
    if any(token in hay for token in ("cron", "schedule", "job", "worker")):
        return "job"
    if "webhook" in hay:
        return "webhook"
    return "unknown"


def _extract_error_frames(text: str) -> list[dict]:
    frames = []
    patterns = [
        re.compile(r'File "([^"]+)", line (\d+)'),
        re.compile(r'([A-Za-z0-9_./\\-]+\.(?:py|js|jsx|ts|tsx|go|rs|rb|java)):(\d+)'),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            frames.append({"file": match.group(1).replace("\\", "/"), "line": int(match.group(2))})
    seen = set()
    unique = []
    for frame in frames:
        key = (frame["file"], frame["line"])
        if key not in seen:
            seen.add(key)
            unique.append(frame)
    return unique


def _extract_http_paths(text: str) -> list[str]:
    paths = []
    for match in re.finditer(r'\b(?:GET|POST|PUT|PATCH|DELETE)\s+(/[A-Za-z0-9_./{}:-]+)', text, flags=re.IGNORECASE):
        paths.append(match.group(1))
    for match in re.finditer(r'\b(/[A-Za-z0-9_./{}:-]+)\b', text):
        path = match.group(1)
        if "/" in path.strip("/") and "." not in path.rsplit("/", 1)[-1]:
            paths.append(path)
    return list(dict.fromkeys(paths))


def _extract_error_terms(text: str) -> list[str]:
    stop = {"file", "line", "error", "exception", "traceback", "returned", "return", "none", "null"}
    terms = []
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text.lower()):
        if token not in stop and not token.isdigit():
            terms.append(token)
    return list(dict.fromkeys(terms))


def _git_diff(repo_root: Path) -> str:
    if not (repo_root / ".git").exists():
        return ""
    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=20,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def _parse_diff_changed_files(diff: str) -> list[str]:
    files = []
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                path = parts[3]
                if path.startswith("b/"):
                    path = path[2:]
                if path != "/dev/null":
                    files.append(path)
        elif line.startswith("+++ b/"):
            files.append(line[6:])
    return list(dict.fromkeys(files))


def _parse_diff_new_ranges(diff: str) -> dict[str, list[tuple[int, int]]]:
    ranges: dict[str, list[tuple[int, int]]] = {}
    current_file = ""
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            current_file = parts[3][2:] if len(parts) >= 4 and parts[3].startswith("b/") else ""
        elif line.startswith("+++ b/"):
            current_file = line[6:]
        elif current_file and line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                length = int(match.group(2) or "1")
                ranges.setdefault(current_file, []).append((start, start + max(length - 1, 0)))
    return ranges


def _symbols_for_changed_files(
    cfg: Config,
    repo_root: Path,
    files: list[str],
    changed_ranges: dict[str, list[tuple[int, int]]],
) -> list[dict]:
    service = RepositoryService(
        repo_root.name,
        repo_root,
        default_branch(repo_root),
        config=cfg,
    )
    ids = [
        record.component_id
        for record in service.index.symbols(service.scope, paths=tuple(files))
    ]
    nodes = service.lookup(ids) if ids else []
    results = []
    for node in nodes:
        meta = node.get("metadata", {})
        file_path = str(meta.get("file", ""))
        line_start = int(meta.get("line_start", 0) or 0)
        line_end = int(meta.get("line_end", 0) or 0)
        ranges = changed_ranges.get(file_path, [])
        if ranges and line_start and line_end:
            overlaps = any(not (end < line_start or start > line_end) for start, end in ranges)
            if not overlaps:
                continue
        results.append({
            "id": node.get("id"),
            "file": file_path,
            "line_start": line_start,
            "line_end": line_end,
            "entry_point": bool(meta.get("entry_point")) or _looks_like_entry_point(node),
            "entry_point_kind": meta.get("entry_point_kind") or _infer_entry_point_kind_from_hit(node),
        })
    results.sort(key=lambda item: (item.get("file") or "", item.get("line_start") or 0, item.get("id") or ""))
    return results


def _has_config_changes(files: list[str]) -> bool:
    names = {Path(path).name for path in files}
    return bool(names & {"pyproject.toml", "package.json", "go.mod", "Cargo.toml", "requirements.txt", "Dockerfile"})


def _has_code_changes(files: list[str]) -> bool:
    return any(Path(path).suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".rb", ".java"} for path in files)


def _limit_list(items: list, max_results: int) -> list:
    return items[:max(1, min(max_results, 500))]


def _normalize_source_signature(source: str) -> str:
    if not source:
        return ""
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
            lines.append(re.sub(r"\s+", " ", stripped))
    return "\n".join(lines[:20])


def _is_test_path(path: str) -> bool:
    p = Path(path)
    parts = set(p.parts)
    return p.name.startswith("test_") or p.name.endswith("_test.py") or "tests" in parts or "__tests__" in parts or ".test." in p.name or ".spec." in p.name


def _node_edges(nodes: list[dict]) -> set[tuple[str, str]]:
    edges = set()
    for node in nodes:
        sid = node.get("id")
        if not sid:
            continue
        for callee in _parse_json_list(node.get("metadata", {}).get("calls", "")):
            edges.add((sid, callee))
    return edges


def _stable_id_moves(before: dict[str, dict], after: dict[str, dict], removed: list[str], added: list[str]) -> list[dict]:
    before_by_stable = {
        node.get("metadata", {}).get("stable_symbol_id"): sid
        for sid, node in before.items()
        if sid in removed and node.get("metadata", {}).get("stable_symbol_id")
    }
    after_by_stable = {
        node.get("metadata", {}).get("stable_symbol_id"): sid
        for sid, node in after.items()
        if sid in added and node.get("metadata", {}).get("stable_symbol_id")
    }
    moves = []
    for stable_id in sorted(set(before_by_stable) & set(after_by_stable)):
        moves.append({
            "stable_symbol_id": stable_id,
            "before": before_by_stable[stable_id],
            "after": after_by_stable[stable_id],
        })
    return moves


def _extract_graphql_operations(text: str) -> list[str]:
    ops = []
    for match in re.finditer(r"\b(?:query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        ops.append(match.group(1))
    return list(dict.fromkeys(ops))


def _looks_like_client_symbol(node: dict) -> bool:
    hay = " ".join([node.get("id", ""), node.get("document", ""), str(node.get("metadata", {}).get("file", ""))]).lower()
    return any(token in hay for token in ("fetch", "axios", "client", "api.ts", "api.js", "request"))


def _repo_nodes_for_graph(info: dict) -> list[dict]:
    if "nodes" in info:
        return info.get("nodes", [])
    root = info.get("root")
    cfg = info.get("config")
    if not root or not cfg:
        return []
    try:
        repo_root = Path(root)
        service = RepositoryService(
            repo_root.name,
            repo_root,
            default_branch(repo_root),
            config=cfg,
        )
        ids = [record.component_id for record in service.index.symbols(service.scope)]
        return service.lookup(ids) if ids else []
    except Exception:
        return []


def _parse_json_list(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
