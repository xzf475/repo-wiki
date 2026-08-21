# indexer/rest_api.py
from __future__ import annotations
import asyncio
import hmac
import json
import logging
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.parse
from pathlib import Path

from indexer.utils import load_env_file
try:
    load_env_file()
except Exception:
    pass

logger = logging.getLogger("repo-wiki-api")

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

from indexer.config import load_config, save_config
from indexer.retrieval import (
    truncate_documents,
    get_edit_context as _get_edit_context_impl,
    find_tests_for_symbol as _find_tests_for_symbol_impl,
    get_index_status as _get_index_status_impl,
    resolve_symbol as _resolve_symbol_impl,
    pre_edit_check as _pre_edit_check_impl,
    impact_analysis as _impact_analysis_impl,
    change_plan as _change_plan_impl,
    diagnose_index as _diagnose_index_impl,
    agent_protocol_bundle as _agent_protocol_bundle_impl,
    locate_from_error as _locate_from_error_impl,
    list_entry_points as _list_entry_points_impl,
    post_edit_verify as _post_edit_verify_impl,
    change_set as _change_set_impl,
    coverage_map as _coverage_map_impl,
    index_diff_report as _index_diff_report_impl,
    cross_repo_graph as _cross_repo_graph_impl,
    agent_capabilities_manifest as _agent_capabilities_manifest_impl,
    stable_symbol_id as _stable_symbol_id_impl,
)
from indexer.task_store import TaskStore
from indexer.repo_registry import RepoRegistry, _get_repo_lock
from indexer.git_ops import (
    _detect_default_branch, _match_branch_rule, _discover_remote_branches,
    _inject_credentials, _store_credentials, _sanitize_error,
    git_fetch_checkout_pull, git_fetch_refs, GitOperationError,
)
from indexer.agent_contracts import agent_schema as _agent_schema_impl
from indexer.repository_index import RepositoryIndexError
from indexer.repository_service import RepositoryService, default_branch

tasks = TaskStore()
registry = RepoRegistry()
registry._load()
MAX_DIFF_BYTES = int(os.environ.get("REPO_WIKI_MAX_DIFF_BYTES", str(2 * 1024 * 1024)))


async def register_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    url = body.get("url", "")
    name = body.get("name", "")
    username = body.get("username", "")
    password = body.get("password", "")
    token = body.get("token", "")
    description = body.get("description", "")
    if not isinstance(description, str):
        return JSONResponse({"error": "description must be a string"}, status_code=400)
    tags = body.get("tags", [])
    if not isinstance(tags, list):
        return JSONResponse({"error": "tags must be a list"}, status_code=400)
    if tags and not all(isinstance(t, str) for t in tags):
        return JSONResponse({"error": "tags must be a list of strings"}, status_code=400)
    branch = body.get("branch", "")
    branches = body.get("branches", [])
    if not isinstance(branches, list):
        return JSONResponse({"error": "branches must be a list"}, status_code=400)
    branch_rule = body.get("branch_rule", "")
    enrich = body.get("enrich", False)
    if not isinstance(enrich, bool):
        return JSONResponse({"error": "enrich must be a boolean"}, status_code=400)

    if not branches and branch:
        branches = [branch]

    # If a branch rule is specified, discover matching branches from remote
    if not url:
        return JSONResponse({"error": "url is required"}, status_code=400)

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme == "http" and (username or password or token):
        return JSONResponse({"error": "http URLs cannot be used with credentials; use https"}, status_code=400)
    if parsed_url.scheme not in ("https", "git", "ssh", "http"):
        return JSONResponse({"error": f"Unsupported URL scheme: {parsed_url.scheme}. Use https, git, ssh, or http."}, status_code=400)
    if branch_rule and not branches:
        discovered = _discover_remote_branches(url, branch_rule)
        if not discovered:
            return JSONResponse({"error": f"no remote branches match pattern '{branch_rule}'"}, status_code=400)
        branches = discovered

    if not name:
        repo_name = parsed_url.path.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        name = repo_name

    if not re.match(r'^[a-zA-Z0-9._-]+$', name) or name in (".", "..") or name.startswith("-"):
        return JSONResponse({"error": "name must contain only alphanumeric, dot, hyphen, underscore"}, status_code=400)

    with registry._lock:
        existing = registry.get(name)
        if existing:
            return JSONResponse({
                "error": f"repo '{name}' already registered",
                "existing": str(existing["root"]),
            }, status_code=409)

        task_id = tasks.create(name, url)

        clone_dir = registry.repos_dir / name
        clone_dir.mkdir(parents=True, exist_ok=True)
        branches_list = branches
        registry.register(name, clone_dir, url=url, branches=branches_list, branch_rule=branch_rule, description=description, tags=tags)

    webhook_url = _get_webhook_url(name)

    first_branch = branches[0] if branches else ""

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        None,
        _run_register_task,
        task_id, name, url, username, password, token, first_branch, enrich, branch_rule,
    )

    return JSONResponse({
        "task_id": task_id,
        "name": name,
        "status": "pending",
        "branches": branches_list,
        "branch_rule": branch_rule or None,
        "webhook_url": webhook_url,
        "webhook_hint": "Configure this URL in your repo's webhook settings (push events) for auto-sync. Set WEBHOOK_SECRET env var for payload verification."
    })


async def task_status(request: Request) -> JSONResponse:
    task_id = request.path_params.get("task_id", "")
    task = tasks.get(task_id)
    if not task:
        return JSONResponse({"error": f"task '{task_id}' not found"}, status_code=404)
    return JSONResponse({k: v for k, v in task.items() if not k.startswith("_")})


async def validate_repo(request: Request) -> JSONResponse:
    name = request.path_params.get("name", "")
    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    root = info["root"]
    cfg = info["config"]
    branches = info.get("branches", []) or [default_branch(root)]
    try:
        services = [
            RepositoryService(name, root, branch, config=cfg)
            for branch in branches
        ]
        statuses = [service.inspect() for service in services]
        integrity = services[0].index.integrity() if services else None
    except RepositoryIndexError as error:
        return JSONResponse({
            "config_file": (root / ".indexer.toml").exists(),
            "index_database": (root / ".indexer" / "state" / "repository-index.sqlite3").exists(),
            "wiki_index": (root / cfg.wiki_dir / "INDEX.md").exists(),
            "skill_file": (root / ".indexer" / "skills" / "codebase.md").exists(),
            "branches": [],
            "tracked_files": 0,
            "total_symbols": 0,
            "stale_count": 0,
            "dense_ready": False,
            "database_integrity": {
                "ok": False,
                "message": str(error),
                "foreign_key_violations": 0,
            },
            "healthy": False,
        })
    checks = {
        "config_file": (root / ".indexer.toml").exists(),
        "index_database": (root / ".indexer" / "state" / "repository-index.sqlite3").exists(),
        "wiki_index": (root / cfg.wiki_dir / "INDEX.md").exists(),
        "skill_file": (root / ".indexer" / "skills" / "codebase.md").exists(),
        "branches": statuses,
        "tracked_files": sum(int(status["indexed_files"]) for status in statuses),
        "total_symbols": sum(int(status["symbols"]) for status in statuses),
        "stale_count": sum(int(status["stale_file_count"]) for status in statuses),
        "dense_ready": all(status["dense_state"] == "ready" for status in statuses),
        "database_integrity": {
            "ok": integrity.ok,
            "message": integrity.message,
            "foreign_key_violations": integrity.foreign_key_violations,
        } if integrity else None,
    }
    checks["healthy"] = bool(
        checks["config_file"]
        and checks["index_database"]
        and checks["wiki_index"]
        and checks["skill_file"]
        and integrity is not None
        and integrity.ok
        and statuses
        and all(status["generation"] is not None for status in statuses)
        and checks["stale_count"] == 0
    )
    return JSONResponse(checks)


async def sync_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    enrich = body.get("enrich", False)
    branch = body.get("branch", "")
    if not isinstance(enrich, bool):
        return JSONResponse({"error": "enrich must be a boolean"}, status_code=400)

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    # If branch is not in the registered list, auto-register it first
    if branch:
        existing_branches = info.get("branches", [])
        if branch not in existing_branches:
            updated_branches = list(existing_branches) + [branch]
            registry.register(name, info["root"], url=info.get("url", ""),
                              branches=updated_branches,
                              branch_rule=info.get("branch_rule", ""),
                              description=info.get("description", ""),
                              tags=info.get("tags", []))

    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_sync_task, task_id, name, info["root"], enrich, branch)

    return JSONResponse({"task_id": task_id, "name": name, "status": "pending"})


def _run_all_branches(
    name: str,
    branches: list[str],
    task_id: str,
    *,
    root: Path,
    enrich: bool = False,
    _skip_lock: bool = False,
):
    lock = _get_repo_lock(name)
    if not _skip_lock and not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        root = Path(root).resolve()
        tasks.update(task_id, status="running", progress=5, step="git_fetch")
        git_fetch_refs(root)

        branch_results: dict[str, dict] = {}
        for position, branch in enumerate(branches, 1):
            tasks.update(
                task_id,
                status="running",
                progress=10 + int(80 * (position - 1) / max(1, len(branches))),
                step=f"{branch}:sync",
            )
            service = RepositoryService(name, root, branch, config=load_config(root))
            result = service.sync(enrich=enrich)
            status = service.index.inspect(service.scope)
            branch_results[branch] = {
                **result,
                "files": status.files,
                "symbols": status.symbols,
            }
        tasks.update(task_id, status="running", progress=95, step="project")
        projection = RepositoryService(
            name,
            root,
            branches[0],
            config=load_config(root),
        ).project()
        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name,
            "path": str(root),
            "indexed_branches": list(branches),
            "skipped_branches": [],
            "max_concurrency": 1,
            "branches": branch_results,
            "projection_branch": branches[0],
            "projection": projection,
            "symbol_count": sum(item["symbols"] for item in branch_results.values()),
        })
    except GitOperationError as exc:
        tasks.update(task_id, status="failed", progress=5, step=f"git_{exc.step}", error=exc.stderr)
    except Exception as exc:
        tasks.update(task_id, status="failed", progress=0, step="branch_index", error=str(exc))
    finally:
        if not _skip_lock:
            lock.release()


async def sync_all_branches(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    enrich = body.get("enrich", False)
    if not isinstance(enrich, bool):
        return JSONResponse({"error": "enrich must be a boolean"}, status_code=400)

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    # Re-discover branches if branch_rule is set
    branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")
    if branch_rule and info.get("url"):
        discovered = _discover_remote_branches(
            info["url"],
            branch_rule,
            cwd=Path(info["root"]),
        )
        if discovered:
            branches = discovered
            registry.register(name, info["root"], url=info.get("url", ""), branches=branches, branch_rule=branch_rule)

    if not branches:
        return JSONResponse({"error": f"no branches to sync for '{name}'"}, status_code=400)

    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        None,
        lambda: _run_all_branches(
            name,
            branches,
            task_id,
            root=info["root"],
            enrich=enrich,
        ),
    )

    return JSONResponse({"task_id": task_id, "name": name, "branches": branches, "status": "pending"})


async def update_repo_and_sync(request: Request) -> JSONResponse:
    """Atomically update repo metadata, discover branches, and synchronize them."""
    repo_name = request.path_params.get("name", "")
    info = registry.get(repo_name)
    if not info:
        return JSONResponse({"error": f"repo '{repo_name}' not registered"}, status_code=404)

    body = await _parse_body(request)
    description = body.get("description")
    tags = body.get("tags")
    branch_rule = body.get("branch_rule")
    enrich = body.get("enrich", False)
    if not isinstance(enrich, bool):
        return JSONResponse({"error": "enrich must be a boolean"}, status_code=400)
    if branch_rule is not None and not isinstance(branch_rule, str):
        return JSONResponse({"error": "branch_rule must be a string"}, status_code=400)

    # 1. Validate branch discovery before changing metadata or scheduling work.
    url = info.get("url", "")
    discovered_branches: list[str] | None = None
    if branch_rule:
        if not url:
            return JSONResponse({"error": "branch_rule requires a remote repository URL"}, status_code=400)
        discovered_branches = _discover_remote_branches(
            url,
            branch_rule,
            cwd=Path(info["root"]),
        )
        if not discovered_branches:
            return JSONResponse(
                {"error": f"no remote branches match pattern '{branch_rule}'"},
                status_code=400,
            )

    # 2. Update meta
    if description is not None or tags is not None or branch_rule is not None:
        registry.update_meta(repo_name, description=description, tags=tags, branch_rule=branch_rule)

    # 3. Register the discovered branches.
    if discovered_branches is not None:
        updated_meta = registry.get(repo_name) or info
        registry.register(
            repo_name,
            info["root"],
            url=url,
            branches=discovered_branches,
            branch_rule=branch_rule,
            description=updated_meta.get("description", ""),
            tags=updated_meta.get("tags", []),
        )

    # 4. Synchronize all branches
    updated_info = registry.get(repo_name)
    branches_to_sync = updated_info.get("branches", []) if updated_info else []
    if not branches_to_sync:
        return JSONResponse({"error": f"no branches to sync for '{repo_name}'"}, status_code=400)

    task_id = tasks.create(repo_name, url)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        None,
        lambda: _run_all_branches(
            repo_name,
            branches_to_sync,
            task_id,
            root=updated_info["root"],
            enrich=enrich,
        ),
    )

    return JSONResponse({
        "task_id": task_id,
        "name": repo_name,
        "branches": branches_to_sync,
        "status": "pending",
    })


def _run_sync_task_inner(task_id: str, name: str, root: Path, enrich: bool, branch: str = "", repo_url: str = "", repo_branches: list[str] | None = None) -> None:
    selected_branch = branch or (
        repo_branches[0] if repo_branches else default_branch(root)
    )
    try:
        tasks.update(task_id, status="running", progress=10, step="git_fetch")
        git_fetch_refs(root)
        cfg = load_config(root)
        if not (root / ".indexer.toml").exists():
            save_config(root, cfg)
        service = RepositoryService(name, root, selected_branch, config=cfg)
        tasks.update(task_id, status="running", progress=40, step="sync")
        result = service.sync(enrich=enrich)
        projection = service.project()
        status = service.index.inspect(service.scope)
        registered = registry.get(name) or {}
        registry.register(
            name,
            root,
            url=repo_url or registered.get("url", ""),
            branches=repo_branches or [selected_branch],
            branch_rule=registered.get("branch_rule", ""),
            description=registered.get("description", ""),
            tags=registered.get("tags", []),
        )
        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name,
            "path": str(root),
            "branch": selected_branch,
            "generation": status.generation,
            "tree_id": status.tree_id,
            "symbol_count": status.symbols,
            "dense_state": status.dense_state,
            "sync": result,
            "projection": projection,
            "webhook_url": _get_webhook_url(name),
        })
    except GitOperationError as error:
        tasks.update(task_id, status="failed", progress=10, step=f"git_{error.step}", error=error.stderr)
    except Exception as error:
        tasks.update(
            task_id,
            status="failed",
            progress=0,
            step="sync",
            error=_sanitize_error(str(error), repo_url, "", "", ""),
        )



def _run_sync_task(task_id: str, name: str, root: Path, enrich: bool, branch: str = "", _skip_lock: bool = False) -> None:
    lock = _get_repo_lock(name)
    if not _skip_lock and not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        existing = registry.get(name)
        repo_url = existing.get("url", "") if existing else ""
        repo_branches = existing.get("branches", []) if existing else []
        _run_sync_task_inner(
            task_id,
            name,
            root,
            enrich,
            branch=branch,
            repo_url=repo_url,
            repo_branches=repo_branches,
        )
    finally:
        if not _skip_lock:
            lock.release()


def _run_register_task(
    task_id: str,
    name: str,
    url: str,
    username: str,
    password: str,
    token: str,
    branch: str,
    enrich: bool,
    branch_rule: str = "",
) -> None:
    lock = _get_repo_lock(name)
    if not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        _run_register_task_inner(task_id, name, url, username, password, token, branch, enrich, branch_rule)
    finally:
        lock.release()


def _run_register_task_inner(
    task_id: str,
    name: str,
    url: str,
    username: str,
    password: str,
    token: str,
    branch: str,
    enrich: bool,
    branch_rule: str = "",
) -> None:
    clone_url = _inject_credentials(url, username, password, token)
    clone_dir = registry.repos_dir / name

    from indexer.git import _GIT_ENV
    git_env = _GIT_ENV

    try:
        if clone_dir.exists() and (clone_dir / ".git").exists():
            tasks.update(task_id, status="running", progress=10, step="git_fetch")
            try:
                git_fetch_checkout_pull(
                    clone_dir, branch,
                    sanitize_fn=lambda s: _sanitize_error(s, url, username, password, token),
                    destructive=True,
                )
            except GitOperationError as e:
                tasks.update(task_id, status="failed", progress=10, step=f"git_{e.step}", error=e.stderr)
                registry.unregister(name)
                if clone_dir.exists():
                    shutil.rmtree(clone_dir)
                return
        else:
            tasks.update(task_id, status="running", progress=10, step="git_clone")
            if clone_dir.exists():
                shutil.rmtree(clone_dir)

            clone_cmd = ["git", "-c", "http.followRedirects=true", "clone"]
            # Clone all branches by default (no --branch flag)
            clone_cmd.extend([clone_url, str(clone_dir)])

            result = subprocess.run(
                clone_cmd, capture_output=True, text=True, timeout=120, env=git_env,
            )
            if result.returncode != 0:
                safe_err = _sanitize_error(result.stderr, url, username, password, token)
                tasks.update(task_id, status="failed", progress=10, step="git_clone", error=safe_err)
                registry.unregister(name)
                if clone_dir.exists():
                    shutil.rmtree(clone_dir)
                return

        _store_credentials(clone_dir, url, username, password, token)

        from indexer.git import is_git_repo
        from indexer.cli import _ensure_cache_gitignore
        from indexer.hooks import install_hook

        root = clone_dir

        registered = registry.get(name)
        configured_branches = list(registered.get("branches", [])) if registered else []
        detected_branch = _detect_default_branch(clone_dir) if is_git_repo(clone_dir) else ""
        if detected_branch and not branch:
            branch = detected_branch

        tasks.update(task_id, status="running", progress=30, step="init")
        cfg = load_config(root)
        save_config(root, cfg)
        _ensure_cache_gitignore(root, verbose=False)
        if is_git_repo(root) and cfg.pre_commit:
            install_hook(root)

        tasks.update(task_id, status="running", progress=35, step="detecting_files")
        # If branch_rule is set, discover and register all matching branches
        if branch_rule and url:
            discovered = _discover_remote_branches(url, branch_rule, cwd=clone_dir)
            if discovered:
                configured_branches = discovered
            else:
                logger.warning("No branches matched branch_rule '%s' for repo %s", branch_rule, name)

        branches_to_index = configured_branches or ([branch] if branch else [])
        registry.register(
            name,
            clone_dir,
            url=url,
            branches=branches_to_index,
            branch_rule=branch_rule,
            description=registered.get("description", "") if registered else "",
            tags=registered.get("tags", []) if registered else [],
        )

        if not branches_to_index:
            tasks.update(task_id, status="completed", progress=100, step="complete", result={
                "name": name, "path": str(clone_dir), "indexed": False, "warning": "No branches to index",
            })
            return

        if len(branches_to_index) > 1:
            _run_all_branches(
                name,
                branches_to_index,
                task_id,
                _skip_lock=True,
                root=root,
                enrich=enrich,
            )
            branch_task = tasks.get(task_id) or {}
            if branch_task.get("status") == "failed":
                return
            result = dict(branch_task.get("result") or {})
            result.update({
                "name": name,
                "path": str(clone_dir),
                "url": url,
                "indexed": True,
                "webhook_url": _get_webhook_url(name),
            })
            tasks.update(task_id, status="completed", progress=100, step="complete", result=result)
            return

        current_branch = branches_to_index[0]
        service = RepositoryService(name, root, current_branch, config=cfg)
        tasks.update(task_id, status="running", progress=50, step=f"{current_branch}:sync")
        sync_result = service.sync(enrich=enrich)
        projection = service.project()
        status = service.index.inspect(service.scope)

        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name,
            "path": str(clone_dir),
            "url": url,
            "branch": current_branch,
            "generation": status.generation,
            "tree_id": status.tree_id,
            "dense_state": status.dense_state,
            "symbol_count": status.symbols,
            "sync": sync_result,
            "projection": projection,
            "indexed": True,
            "webhook_url": _get_webhook_url(name),
        })

    except subprocess.TimeoutExpired as e:
        cmd = e.cmd[0] if hasattr(e, 'cmd') else "git"
        tasks.update(task_id, status="failed", progress=0, step=cmd, error=f"timeout: {cmd} took too long")
    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=_sanitize_error(str(e), url, username, password, token))


async def unregister_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    registry.unregister(name)

    return JSONResponse({"name": name, "unregistered": True})


async def search_symbols(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    query = body.get("query", "")
    repo = body.get("repo")
    requested_branch = body.get("branch", "")
    if not isinstance(requested_branch, str):
        return JSONResponse({"error": "branch must be a string"}, status_code=400)
    try:
        top_k = max(1, min(int(body.get("top_k", 10)), 100))
        expand_depth = max(0, min(int(body.get("expand_depth", 1)), 5))
    except (ValueError, TypeError):
        return JSONResponse({"error": "top_k and expand_depth must be integers"}, status_code=400)
    retrieval = body.get("retrieval", "preferred")
    if retrieval not in {"local", "preferred", "required"}:
        return JSONResponse({
            "error": "retrieval must be local, preferred, or required",
        }, status_code=400)

    if not query:
        return JSONResponse({"error": "query is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": "no repos available"}, status_code=404)

    ambiguous = [
        name for name, info in targets
        if len(info.get("branches", [])) > 1 and not requested_branch
    ]
    if ambiguous:
        return JSONResponse({
            "error": "branch is required for multi-branch repositories",
            "repos": ambiguous,
        }, status_code=400)
    invalid = [
        name for name, info in targets
        if requested_branch
        and info.get("branches", [])
        and requested_branch not in info.get("branches", [])
    ]
    if invalid:
        return JSONResponse({
            "error": f"branch '{requested_branch}' is not registered",
            "repos": invalid,
        }, status_code=400)

    all_hits = []
    all_related = []
    search_metrics = []
    seen_matches: set[tuple[str, str, str]] = set()
    seen_related: set[tuple[str, str, str]] = set()
    for name, info in targets:
        cfg = info["config"]
        root = info["root"]
        repo_branches = info.get("branches", [])
        branch = requested_branch or (
            repo_branches[0] if repo_branches else default_branch(root)
        )
        service = RepositoryService(name, root, branch, config=cfg)
        try:
            response = service.search(
                query,
                limit=top_k,
                related_limit=top_k if expand_depth else 0,
                retrieval=retrieval,
            )
        except RepositoryIndexError as error:
            status_code = 503 if error.code == "HYBRID_REQUIRED_UNAVAILABLE" else 404
            if error.code == "INVALID_REQUEST":
                status_code = 400
            return JSONResponse({
                "error": str(error),
                "code": error.code,
                "phase": error.phase,
                "repo": name,
                "branch": branch,
            }, status_code=status_code)
        search_metrics.append({
            "repo": name,
            "branch": branch,
            "query": query,
            **response["search_metrics"],
        })
        for hit in response["matches"]:
            key = (name, branch, hit["id"])
            if key in seen_matches:
                continue
            seen_matches.add(key)
            item = dict(hit)
            item["repo"] = name
            item["branch"] = branch
            all_hits.append(item)
        related_items = list(response["related"])
        if expand_depth > 1:
            expanded_ids = {item["id"] for item in related_items}
            for hit in response["matches"]:
                for related in service.trace(
                    hit["id"],
                    direction="down",
                    max_depth=expand_depth,
                )[1:]:
                    if related["id"] in expanded_ids:
                        continue
                    related["relation"] = "call"
                    related_items.append(related)
                    expanded_ids.add(related["id"])
                    if len(related_items) >= top_k:
                        break
        for related in related_items[:top_k]:
            key = (name, branch, related["id"])
            if key in seen_matches or key in seen_related:
                continue
            seen_related.add(key)
            item = dict(related)
            item["repo"] = name
            item["branch"] = branch
            all_related.append(item)

    truncate_documents(all_hits)
    truncate_documents(all_related)
    all_hits.sort(key=lambda hit: (-float(hit.get("score", 0.0)), hit.get("repo", ""), hit.get("id", "")))
    all_hits = all_hits[:top_k]

    return JSONResponse({
        "results": all_hits,
        "matches": all_hits,
        "related": all_related,
        "total": len(all_hits),
        "search_metrics": search_metrics,
        "index_status": [
            RepositoryService(
                name,
                info["root"],
                requested_branch or (
                    info.get("branches", [""])[0]
                    if info.get("branches")
                    else default_branch(info["root"])
                ),
                config=info["config"],
            ).inspect()
            for name, info in targets
        ],
    })


async def trace_call(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    direction = body.get("direction", "down")
    try:
        max_depth = max(1, min(int(body.get("max_depth", 3)), 8))
    except (ValueError, TypeError):
        return JSONResponse({"error": "max_depth must be an integer"}, status_code=400)
    repo = body.get("repo")
    requested_branch = body.get("branch", "")
    if not isinstance(requested_branch, str):
        return JSONResponse({"error": "branch must be a string"}, status_code=400)

    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    all_nodes = []
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": "no repos available"}, status_code=404)
    ambiguous = [
        name for name, info in targets
        if len(info.get("branches", [])) > 1 and not requested_branch
    ]
    if ambiguous:
        return JSONResponse({
            "error": "branch is required for multi-branch repositories",
            "repos": ambiguous,
        }, status_code=400)
    invalid = [
        name for name, info in targets
        if requested_branch
        and info.get("branches", [])
        and requested_branch not in info.get("branches", [])
    ]
    if invalid:
        return JSONResponse({
            "error": f"branch '{requested_branch}' is not registered",
            "repos": invalid,
        }, status_code=400)

    for name, info in targets:
        branches = info.get("branches", [])
        branch = requested_branch or (
            branches[0] if branches else default_branch(info["root"])
        )
        nodes = RepositoryService(
            name,
            info["root"],
            branch,
            config=info["config"],
        ).trace(symbol_id, direction=direction, max_depth=max_depth)
        for n in nodes:
            n["repo"] = name
            n["branch"] = branch
        all_nodes.extend(nodes)

    return JSONResponse({"results": all_nodes, "total": len(all_nodes)})


async def get_source_context(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    file_path = body.get("file_path", "")
    try:
        line_start = int(body.get("line_start", 1))
        line_end = int(body.get("line_end", 1))
        padding = min(int(body.get("padding", 5)), 50)
    except (ValueError, TypeError):
        return JSONResponse({"error": "line_start, line_end, and padding must be integers"}, status_code=400)
    repo = body.get("repo")

    if not file_path or not repo:
        return JSONResponse({"error": "file_path and repo are required"}, status_code=400)

    info = registry.get(repo)
    if not info:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    root = info["root"]
    abs_path = (root / file_path).resolve()
    root_resolved = root.resolve()

    if not abs_path.is_relative_to(root_resolved):
        return JSONResponse({"error": "access denied: path outside repo root"}, status_code=403)

    if not abs_path.exists():
        return JSONResponse({"error": f"file not found: {file_path}"}, status_code=404)

    try:
        lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return JSONResponse({"error": f"cannot read file: {file_path}"}, status_code=500)

    start = max(1, line_start - padding) - 1
    end = min(len(lines), line_end + padding)
    # Anti-scraping: hard cap total returned lines
    MAX_LINES = 500
    if end - start > MAX_LINES:
        end = start + MAX_LINES
    selected = lines[start:end]
    numbered = [f"{i+1:>4} | {line}" for i, line in zip(range(start, end), selected)]

    return JSONResponse({
        "file_path": file_path,
        "repo": repo,
        "line_start": line_start,
        "line_end": line_end,
        "source": "\n".join(numbered),
        "total_lines": len(lines),
    })


async def get_edit_context(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    try:
        padding = max(0, min(int(body.get("padding", 8)), 50))
    except (TypeError, ValueError):
        return JSONResponse({"error": "padding must be an integer"}, status_code=400)

    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    context = _get_edit_context_impl(symbol_id, info["config"], info["root"], padding=padding)
    context["repo"] = name
    status = 404 if context.get("error") else 200
    return JSONResponse(context, status_code=status)


async def resolve_symbol(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    query = body.get("query", "")
    repo = body.get("repo")
    file_hint = body.get("file_hint", "")
    type_hint = body.get("type_hint", "")
    try:
        top_k = max(1, min(int(body.get("top_k", 10)), 50))
    except (TypeError, ValueError):
        return JSONResponse({"error": "top_k must be an integer"}, status_code=400)

    if not query:
        return JSONResponse({"error": "query is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _resolve_symbol_impl(query, info["config"], info["root"], file_hint=file_hint, type_hint=type_hint, top_k=top_k)
    result["repo"] = name
    result["index_status"] = _get_index_status_impl(info["root"])
    return JSONResponse(result)


async def find_tests_for_symbol(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    try:
        max_results = max(1, min(int(body.get("max_results", 10)), 50))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)

    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    results = []
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    for name, info in targets:
        matches = _find_tests_for_symbol_impl(symbol_id, info["config"], info["root"], max_results=max_results)
        for match in matches:
            match["repo"] = name
        results.extend(matches)

    results.sort(key=lambda item: (-item.get("score", 0), item.get("repo", ""), item.get("file", "")))
    results = results[:max_results]
    return JSONResponse({"results": results, "total": len(results)})


async def pre_edit_check(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _pre_edit_check_impl(symbol_id, info["config"], info["root"])
    result["repo"] = name
    return JSONResponse(result)


async def impact_analysis(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    try:
        max_depth = max(1, min(int(body.get("max_depth", 2)), 5))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_depth must be an integer"}, status_code=400)
    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _impact_analysis_impl(symbol_id, info["config"], info["root"], max_depth=max_depth)
    result["repo"] = name
    status = 404 if result.get("error") else 200
    return JSONResponse(result, status_code=status)


async def change_plan(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    goal = body.get("goal", "")
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    if not goal:
        return JSONResponse({"error": "goal is required"}, status_code=400)
    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _change_plan_impl(goal, symbol_id, info["config"], info["root"])
    result["repo"] = name
    return JSONResponse(result)


async def diagnose_index(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    reports = []
    for name, info in targets:
        report = _diagnose_index_impl(info["root"], info["config"])
        report["repo"] = name
        reports.append(report)

    if repo:
        return JSONResponse(reports[0])
    return JSONResponse({"results": reports, "total": len(reports)})


async def agent_protocol(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    goal = body.get("goal", "")
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    protocol = body.get("protocol", "codex")
    if not goal:
        return JSONResponse({"error": "goal is required"}, status_code=400)
    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _agent_protocol_bundle_impl(goal, symbol_id, info["config"], info["root"], protocol=protocol)
    result["repo"] = name
    return JSONResponse(result)


async def locate_from_error(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    error_text = body.get("error_text", "")
    repo = body.get("repo")
    try:
        top_k = max(1, min(int(body.get("top_k", 10)), 50))
    except (TypeError, ValueError):
        return JSONResponse({"error": "top_k must be an integer"}, status_code=400)
    if not error_text:
        return JSONResponse({"error": "error_text is required"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    all_candidates = []
    payloads = []
    for name, info in targets:
        result = _locate_from_error_impl(error_text, info["config"], info["root"], top_k=top_k)
        for candidate in result.get("candidates", []):
            candidate["repo"] = name
            all_candidates.append(candidate)
        result["repo"] = name
        payloads.append(result)

    all_candidates.sort(key=lambda item: (-item.get("locate_score", 0), item.get("repo", ""), item.get("id", "")))
    return JSONResponse({
        "candidates": all_candidates[:top_k],
        "total": min(len(all_candidates), top_k),
        "results": payloads,
    })


async def list_entry_points(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    kind = body.get("kind", "")
    try:
        max_results = max(1, min(int(body.get("max_results", 50)), 200))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    all_results = []
    payloads = []
    for name, info in targets:
        result = _list_entry_points_impl(info["config"], info["root"], kind=kind, max_results=max_results)
        for entry in result.get("results", []):
            entry["repo"] = name
            all_results.append(entry)
        result["repo"] = name
        payloads.append(result)

    all_results.sort(key=lambda item: (item.get("kind", ""), item.get("repo", ""), item.get("file") or ""))
    if repo:
        return JSONResponse(payloads[0])
    return JSONResponse({"results": all_results[:max_results], "total": min(len(all_results), max_results), "repos": payloads})


async def post_edit_verify(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    diff = body.get("diff", "")
    too_large = _validate_diff_payload(diff)
    if too_large:
        return too_large
    changed_files = body.get("changed_files", [])
    if changed_files and not isinstance(changed_files, list):
        return JSONResponse({"error": "changed_files must be a list"}, status_code=400)
    if changed_files and not all(isinstance(item, str) for item in changed_files):
        return JSONResponse({"error": "changed_files must be a list of strings"}, status_code=400)

    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)

    name, info = targets[0]
    result = _post_edit_verify_impl(info["config"], info["root"], diff=diff, changed_files=changed_files)
    result["repo"] = name
    return JSONResponse(result)


async def change_set(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    goal = body.get("goal", "")
    symbol_id = body.get("symbol_id", "")
    repo = body.get("repo")
    diff = body.get("diff", "")
    too_large = _validate_diff_payload(diff)
    if too_large:
        return too_large
    changed_files = body.get("changed_files", [])
    include_details = bool(body.get("include_details", True))
    try:
        max_results = max(1, min(int(body.get("max_results", 50)), 500))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)
    if not goal:
        return JSONResponse({"error": "goal is required"}, status_code=400)
    if changed_files and not isinstance(changed_files, list):
        return JSONResponse({"error": "changed_files must be a list"}, status_code=400)
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)
    name, info = targets[0]
    result = _change_set_impl(
        goal,
        info["config"],
        info["root"],
        symbol_id=symbol_id,
        diff=diff,
        changed_files=changed_files,
        max_results=max_results,
        include_details=include_details,
    )
    result["repo"] = name
    return JSONResponse(result)


async def coverage_map(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    symbol_id = body.get("symbol_id", "")
    try:
        max_results = max(1, min(int(body.get("max_results", 100)), 500))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)
    name, info = targets[0]
    result = _coverage_map_impl(info["config"], info["root"], symbol_id=symbol_id, max_results=max_results)
    result["repo"] = name
    return JSONResponse(result)


async def index_diff_report(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    before_nodes = body.get("before_nodes", [])
    after_nodes = body.get("after_nodes", [])
    if not isinstance(before_nodes, list) or not isinstance(after_nodes, list):
        return JSONResponse({"error": "before_nodes and after_nodes must be lists"}, status_code=400)
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)
    if repo is None and len(targets) != 1:
        return JSONResponse({"error": "repo is required when multiple repos are registered"}, status_code=400)
    name, info = targets[0]
    result = _index_diff_report_impl(info["config"], info["root"], before_nodes=before_nodes, after_nodes=after_nodes)
    result["repo"] = name
    return JSONResponse(result)


async def cross_repo_graph(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo_names = body.get("repos", [])
    try:
        max_results = max(1, min(int(body.get("max_results", 200)), 1000))
    except (TypeError, ValueError):
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)
    if repo_names and not isinstance(repo_names, list):
        return JSONResponse({"error": "repos must be a list"}, status_code=400)
    names = repo_names or registry.list_names()
    repos = {}
    for name in names:
        info = registry.get(name)
        if info:
            repos[name] = info
    if not repos:
        return JSONResponse({"error": "no repos available"}, status_code=404)
    return JSONResponse(_cross_repo_graph_impl(repos, max_results=max_results))


async def agent_capabilities(request: Request) -> JSONResponse:
    return JSONResponse(_agent_capabilities_manifest_impl())


async def agent_schema(request: Request) -> JSONResponse:
    return JSONResponse(_agent_schema_impl())


async def stable_symbol_id_endpoint(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)
    return JSONResponse({
        "stable_symbol_id": _stable_symbol_id_impl(
            symbol_id,
            body.get("symbol_type", ""),
            body.get("file_path", ""),
            body.get("source", ""),
        )
    })


async def index_status(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    repo = body.get("repo")
    requested_branch = body.get("branch", "")
    if not isinstance(requested_branch, str):
        return JSONResponse({"error": "branch must be a string"}, status_code=400)
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": f"repo '{repo}' not registered"}, status_code=404)

    statuses = []
    for name, info in targets:
        branches = [requested_branch] if requested_branch else (
            info.get("branches", []) or [default_branch(info["root"])]
        )
        for branch in branches:
            statuses.append(RepositoryService(
                name,
                info["root"],
                branch,
                config=info["config"],
            ).inspect())

    if repo and len(statuses) == 1:
        return JSONResponse(statuses[0])
    return JSONResponse({"results": statuses, "total": len(statuses)})


async def list_repos(request: Request) -> JSONResponse:
    result = []
    for name in registry.list_names():
        info = registry.get(name)
        if not info:
            continue
        root = info["root"]
        branches = info.get("branches", [])
        statuses = [
            RepositoryService(name, root, branch, config=info["config"]).inspect()
            for branch in (branches or [default_branch(root)])
        ]
        webhook_url = _get_webhook_url(name, request)
        result.append({
            "name": name,
            "path": str(root),
            "url": info.get("url", ""),
            "branches": branches,
            "description": info.get("description", ""),
            "tags": info.get("tags", []),
            "webhook_url": webhook_url,
            "dense_ready": all(status["dense_state"] == "ready" for status in statuses),
            "symbol_count": sum(int(status["symbols"]) for status in statuses),
            "generations": {
                status["current_branch"]: status["generation"]
                for status in statuses
            },
            "trees": {
                status["current_branch"]: status["indexed_tree"]
                for status in statuses
            },
        })
    return JSONResponse({"repos": result})


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "repos": len(registry.list_names())})


async def repo_detail(request: Request) -> JSONResponse:
    repo_name = request.path_params.get("name", "")
    info = registry.get(repo_name)
    if not info:
        return JSONResponse({"error": f"repo '{repo_name}' not registered"}, status_code=404)

    root = info["root"]
    cfg = info["config"]

    wiki_dir = root / cfg.wiki_dir
    skill_path = root / ".indexer" / "skills" / "codebase.md"

    wiki_pages = []
    if wiki_dir.exists():
        for md_file in sorted(wiki_dir.glob("*.md")):
            page_name = md_file.stem
            wiki_pages.append({
                "name": page_name,
                "path": str(md_file.relative_to(root)),
                "size": md_file.stat().st_size,
            })

    skill_content = ""
    if skill_path.exists():
        skill_content = skill_path.read_text(encoding="utf-8", errors="replace")

    webhook_url = _get_webhook_url(repo_name, request)

    branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")
    branches_detail = []
    branches_missing = []

    if branch_rule and info.get("url"):
        try:
            discovered = _discover_remote_branches(
                info["url"],
                branch_rule,
                cwd=Path(info["root"]),
            )
            registered_set = set(branches)
            for br in discovered:
                if br not in registered_set:
                    branches_missing.append({"name": br})
        except Exception as e:
            logger.warning("Failed to discover branches for %s: %s", repo_name, e)

    for branch in (branches or [default_branch(root)]):
        status = RepositoryService(repo_name, root, branch, config=cfg).inspect()
        branches_detail.append({
            "name": branch,
            "tree_id": status["indexed_tree"],
            "generation": status["generation"],
            "indexed": status["generation"] is not None,
            "dense_state": status["dense_state"],
            "files": status["indexed_files"],
            "symbols": status["symbols"],
            "is_stale": status["is_stale"],
        })

    return JSONResponse({
        "name": repo_name,
        "path": str(root),
        "url": info.get("url", ""),
        "branches": info.get("branches", []),
        "branches_detail": branches_detail,
        "branches_missing": branches_missing,
        "description": info.get("description", ""),
        "tags": info.get("tags", []),
        "branch_rule": info.get("branch_rule", ""),
        "webhook_url": webhook_url,
        "wiki_pages": wiki_pages,
        "index": branches_detail,
        "skill": skill_content,
        "dense_ready": all(item["dense_state"] == "ready" for item in branches_detail),
    })


async def wiki_page_content(request: Request) -> JSONResponse:
    repo_name = request.path_params.get("name", "")
    page_name = request.path_params.get("page", "")
    info = registry.get(repo_name)
    if not info:
        return JSONResponse({"error": f"repo '{repo_name}' not registered"}, status_code=404)
    root = info["root"]
    cfg = info["config"]
    wiki_dir = root / cfg.wiki_dir
    safe_name = page_name.replace("/", "_").replace("..", "_")
    page_path = wiki_dir / f"{safe_name}.md"
    if not page_path.exists():
        return JSONResponse({"error": f"page '{page_name}' not found"}, status_code=404)
    try:
        content = page_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return JSONResponse({"error": f"failed to read page: {e}"}, status_code=500)
    return JSONResponse({"name": page_name, "content": content})


async def update_repo_meta(request: Request) -> JSONResponse:
    repo_name = request.path_params.get("name", "")
    info = registry.get(repo_name)
    if not info:
        return JSONResponse({"error": f"repo '{repo_name}' not registered"}, status_code=404)

    body = await _parse_body(request)
    description = body.get("description")
    tags = body.get("tags")
    branch_rule = body.get("branch_rule")

    if description is None and tags is None and branch_rule is None:
        return JSONResponse({"error": "no fields to update (send description, tags, and/or branch_rule)"}, status_code=400)

    registry.update_meta(repo_name, description=description, tags=tags, branch_rule=branch_rule)

    return JSONResponse({
        "name": repo_name,
        "description": description if description is not None else info.get("description", ""),
        "tags": tags if tags is not None else info.get("tags", []),
        "branch_rule": branch_rule if branch_rule is not None else info.get("branch_rule", ""),
        "updated": True,
    })


async def multi_repo_skill(request: Request) -> JSONResponse:
    all_repos = []
    for name, info in registry.items():
        root = info["root"]
        cfg = info["config"]
        wiki_dir = root / cfg.wiki_dir
        skill_path = root / ".indexer" / "skills" / "codebase.md"

        wiki_pages = []
        if wiki_dir.exists():
            for md_file in sorted(wiki_dir.glob("*.md")):
                wiki_pages.append({
                    "name": md_file.stem,
                    "path": str(md_file.relative_to(root)),
                })

        branches = info.get("branches", []) or [default_branch(root)]
        statuses = [
            RepositoryService(name, root, branch, config=cfg).inspect()
            for branch in branches
        ]
        total_symbols = sum(int(status["symbols"]) for status in statuses)
        total_files = sum(int(status["indexed_files"]) for status in statuses)
        generations = {
            status["current_branch"]: status["generation"]
            for status in statuses
        }
        trees = {
            status["current_branch"]: status["indexed_tree"]
            for status in statuses
        }

        skill_content = ""
        if skill_path.exists():
            skill_content = skill_path.read_text(encoding="utf-8", errors="replace")

        all_repos.append({
            "name": name,
            "path": str(root),
            "total_symbols": total_symbols,
            "total_files": total_files,
            "generations": generations,
            "trees": trees,
            "wiki_pages": wiki_pages,
            "skill": skill_content,
            "dense_ready": all(status["dense_state"] == "ready" for status in statuses),
        })

    if not all_repos:
        return JSONResponse({"error": "No repos registered"}, status_code=404)

    if len(all_repos) == 1:
        return JSONResponse({"skill": all_repos[0]["skill"], "repos": [all_repos[0]["name"]]})

    combined_lines = [
        "---",
        "name: codebase",
        "description: >",
        "  Navigate multiple codebases. Activates when the user asks about code structure",
        "  across repos, where a function lives, how a module works, or cross-repo",
        "  dependencies. Do NOT activate for general programming questions unrelated",
        "  to these specific repos.",
        "---",
        "",
        "# Multi-Repo Codebase Navigation",
        "",
        f"{len(all_repos)} repositories are indexed. **Check the wiki before reading any source file.**",
        "",
        "## Repositories",
        "",
    ]

    for r in all_repos:
        combined_lines.append(f"### {r['name']}")
        combined_lines.append(
            f"- **{r['total_symbols']} symbols** across **{r['total_files']} files**"
            f" — generations {r['generations']}"
        )
        combined_lines.append(f"- Path: `{r['path']}`")
        combined_lines.append(f"- Dense enrichment: {'ready' if r['dense_ready'] else 'not ready'}")

        if r["wiki_pages"]:
            combined_lines.append("- Wiki pages:")
            for wp in r["wiki_pages"]:
                combined_lines.append(f"  - [{wp['name']}]({wp['path']})")
        combined_lines.append("")

    combined_lines.extend([
        "## Workflow — How to Answer Questions Across Repos",
        "",
        "1. **Identify the repo** — Match the question to a repository from the list above.",
        "2. **Read the repo's skill file** — Each repo has its own skill file with detailed navigation instructions.",
        "3. **Use MCP tools** — If MCP is connected to the REST API, use `list_repos` to discover repos,",
        "   `search_symbols_tool` to search (optionally specifying `repo`), `trace_call_tool` and",
        "   `get_source_context_tool` to drill down.",
        "4. **Cross-repo search** — Omit the `repo` parameter in search to search across all repos at once.",
        "",
        "## Per-Repo Skill Files",
        "",
    ])

    for r in all_repos:
        if r["skill"]:
            combined_lines.append(f"### {r['name']}")
            combined_lines.append("```")
            combined_lines.append(r["skill"])
            combined_lines.append("```")
            combined_lines.append("")

    combined_lines.extend([
        "## Component ID Format",
        "",
        "```",
        "repo_name:path/to/file.py::ClassName.method_name",
        "```",
        "",
        "When working across repos, prefix the component ID with the repo name to disambiguate.",
        "",
    ])

    skill_text = "\n".join(combined_lines)
    return JSONResponse({
        "skill": skill_text,
        "repos": [r["name"] for r in all_repos],
    })


def _get_webhook_url(name: str, request: Request | None = None) -> str:
    domain = os.environ.get("PUBLIC_DOMAIN", "").rstrip("/")
    if not domain and request is not None:
        base = str(request.base_url).rstrip("/")
        domain = base
    if not domain:
        host = os.environ.get("PUBLIC_HOST", "")
        if host:
            domain = f"https://{host}"
    if not domain:
        return ""
    sign = _webhook_sign(name)
    return f"{domain}/webhook/{name}?sign={sign}"


def _webhook_sign(name: str) -> str:
    secret = os.environ.get("WEBHOOK_SECRET", "")
    if not secret:
        return ""
    import hashlib
    return hmac.new(secret.encode(), name.encode(), hashlib.sha256).hexdigest()


def _verify_webhook_sign(name: str, sign: str) -> bool:
    expected = _webhook_sign(name)
    if not expected:
        return True
    return hmac.compare_digest(expected, sign)


async def webhook_by_name(request: Request) -> JSONResponse:
    name = request.path_params.get("name", "")
    if not name or not registry.get(name):
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    body = await request.body()

    if os.environ.get("WEBHOOK_SECRET", ""):
        sign = request.query_params.get("sign", "")
        if not sign or not _verify_webhook_sign(name, sign):
            return JSONResponse({"error": "invalid sign"}, status_code=401)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": "repo not found"}, status_code=404)
    repo_branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")

    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {}

    ref = payload.get("ref", "")
    webhook_branch = ""
    if ref.startswith("refs/heads/"):
        webhook_branch = ref[len("refs/heads/"):]

    target_branch = ""
    if webhook_branch:
        if not repo_branches or webhook_branch in repo_branches:
            target_branch = webhook_branch
        elif branch_rule and _match_branch_rule(webhook_branch, branch_rule):
            # New branch matching branch_rule — register it and sync
            target_branch = webhook_branch
            if target_branch not in repo_branches:
                repo_branches = list(repo_branches) + [target_branch]
                registry.register(name, info["root"], url=info.get("url", ""), branches=repo_branches, branch_rule=branch_rule)
    logger.info("Webhook triggered: repo=%s branch=%s", name, target_branch or webhook_branch or "(any)")
    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_sync_task, task_id, name, info["root"], True, target_branch)

    return JSONResponse({
        "task_id": task_id,
        "name": name,
        "status": "pending",
        "trigger": "webhook",
        "branch": target_branch or "any",
    })


def create_app(repos: dict[str, Path] | None = None, repos_dir: Path | None = None) -> Starlette:
    if repos_dir:
        registry.repos_dir = repos_dir
        registry._registry_file = repos_dir / "repos_registry.json"
        registry.repos_dir.mkdir(parents=True, exist_ok=True)

    if repos:
        for name, path in repos.items():
            registry.register(name, path, url="", branches=[default_branch(path)])

    from starlette.staticfiles import StaticFiles
    from starlette.middleware import Middleware
    from starlette.middleware.base import BaseHTTPMiddleware
    static_dir = Path(__file__).parent / "static"

    middleware = []
    api_key = os.environ.get("REPO_WIKI_API_KEY")

    # Request logging middleware (IP + method + path + duration)
    class _LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            start = time.time()
            client_ip = request.client.host if request.client else "unknown"
            response = await call_next(request)
            elapsed = time.time() - start
            logger.info("%s %s %s %s %.3fs %s",
                        client_ip, request.method, request.url.path, response.status_code, elapsed,
                        request.url.query if request.url.query else "")
            return response
    middleware.append(Middleware(_LoggingMiddleware))

    if api_key:
        class _AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                path = request.url.path
                if path in ("/health", "/", "/static") or path.startswith(("/webhook/", "/static/")):
                    return await call_next(request)
                token = request.headers.get("Authorization", "")
                if token.lower().startswith("bearer "):
                    token = token[7:]
                if not hmac.compare_digest(token.encode(), api_key.encode()):
                    return JSONResponse({"error": "unauthorized"}, status_code=401)
                return await call_next(request)
        middleware.append(Middleware(_AuthMiddleware))

    async def _invalid_body_handler(request, exc):
        return JSONResponse({"error": str(exc)}, status_code=400)

    app = Starlette(
        middleware=middleware,
        exception_handlers={_InvalidBodyError: _invalid_body_handler},
        routes=[
            Route("/health", health),
            Route("/repos", list_repos),
            Route("/search", search_symbols, methods=["POST"]),
            Route("/trace", trace_call, methods=["POST"]),
            Route("/source", get_source_context, methods=["POST"]),
            Route("/edit-context", get_edit_context, methods=["POST"]),
            Route("/resolve-symbol", resolve_symbol, methods=["POST"]),
            Route("/tests-for-symbol", find_tests_for_symbol, methods=["POST"]),
            Route("/pre-edit-check", pre_edit_check, methods=["POST"]),
            Route("/impact-analysis", impact_analysis, methods=["POST"]),
            Route("/change-plan", change_plan, methods=["POST"]),
            Route("/diagnose-index", diagnose_index, methods=["POST"]),
            Route("/agent-protocol", agent_protocol, methods=["POST"]),
            Route("/locate-from-error", locate_from_error, methods=["POST"]),
            Route("/entry-points", list_entry_points, methods=["POST"]),
            Route("/post-edit-verify", post_edit_verify, methods=["POST"]),
            Route("/change-set", change_set, methods=["POST"]),
            Route("/coverage-map", coverage_map, methods=["POST"]),
            Route("/index-diff-report", index_diff_report, methods=["POST"]),
            Route("/cross-repo-graph", cross_repo_graph, methods=["POST"]),
            Route("/agent-capabilities", agent_capabilities, methods=["GET", "POST"]),
            Route("/agent-schema", agent_schema, methods=["GET", "POST"]),
            Route("/stable-symbol-id", stable_symbol_id_endpoint, methods=["POST"]),
            Route("/index-status", index_status, methods=["POST"]),
            Route("/register", register_repo, methods=["POST"]),
            Route("/unregister", unregister_repo, methods=["POST"]),
            Route("/sync", sync_repo, methods=["POST"]),
            Route("/sync-all", sync_all_branches, methods=["POST"]),
            Route("/webhook/{name}", webhook_by_name, methods=["POST"]),
            Route("/api/repo/{name}", repo_detail),
            Route("/api/repo/{name}", update_repo_meta, methods=["PATCH"]),
            Route("/api/repo/{name}/sync", update_repo_and_sync, methods=["POST"]),
            Route("/api/repo/{name}/wiki/{page}", wiki_page_content),
            Route("/api/validate/{name}", validate_repo),
            Route("/api/task/{task_id}", task_status),
            Route("/skill", multi_repo_skill),
            Route("/", _index_page),
        ],
    )
    app.mount("/static", StaticFiles(directory=str(static_dir)))
    return app


def _index_page(request: Request):
    static_dir = Path(__file__).parent / "static"
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return JSONResponse({"error": "index.html not found"}, status_code=404)
    html = index_path.read_text(encoding="utf-8")
    return HTMLResponse(html)


def _resolve_repos(repo: str | None) -> list[tuple[str, dict]]:
    if repo:
        info = registry.get(repo)
        if not info:
            return []
        return [(repo, info)]
    return registry.items()


class _InvalidBodyError(Exception):
    pass


def _validate_diff_payload(diff: str) -> JSONResponse | None:
    if diff and len(diff.encode("utf-8", errors="replace")) > MAX_DIFF_BYTES:
        return JSONResponse(
            {"error": f"diff payload too large; max {MAX_DIFF_BYTES} bytes"},
            status_code=413,
        )
    return None


async def _parse_body(request: Request) -> dict:
    try:
        body = await request.json()
    except Exception:
        raise _InvalidBodyError("invalid JSON body")
    if not isinstance(body, dict):
        raise _InvalidBodyError("request body must be a JSON object")
    return body
