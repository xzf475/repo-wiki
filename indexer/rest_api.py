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

from indexer.config import Config, load_config, save_config
from indexer.manifest import Manifest
from indexer.embedding import embed_query
from indexer.vector_store import search, get_by_ids
from indexer.retrieval import trace_call as _trace_call_retrieval, _expand_with_call_graph as _expand_retrieval, _parse_json_list, truncate_documents
from indexer.indexing import (
    cross_reference, load_existing_nodes, parse_candidates,
    build_batches, write_wiki_pages, write_index_and_skill,
    update_manifest, upsert_vectors,
)
from indexer.grouper import density_group
from indexer.task_store import TaskStore
from indexer.repo_registry import RepoRegistry, _get_repo_lock, _repo_locks, _locks_lock
from indexer.git_ops import (
    _detect_default_branch, _match_branch_rule, _discover_remote_branches,
    _inject_credentials, _store_credentials, _sanitize_error,
    git_fetch_checkout_pull, GitOperationError,
)

from indexer.utils import FATAL_EXCEPTIONS

tasks = TaskStore()
registry = RepoRegistry()
registry._load()


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
    skip_deep = body.get("skip_deep", True)
    force_reindex = body.get("force_reindex", False)

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
        if existing and not force_reindex:
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
    if not first_branch:
        first_branch = "main"

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        None,
        _run_register_task,
        task_id, name, url, username, password, token, first_branch, skip_deep, force_reindex, branch_rule,
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

    checks = {}

    indexer_toml = root / ".indexer.toml"
    checks["config_file"] = indexer_toml.exists()

    manifest_path = root / ".indexer" / "manifest.json"
    manifest_ok = manifest_path.exists()
    checks["manifest_file"] = manifest_ok
    checks["last_indexed_commit"] = None
    checks["indexed_at"] = None
    checks["tracked_files"] = 0
    checks["total_symbols"] = 0

    manifest_data = None
    if manifest_ok:
        from indexer.manifest import load_manifest
        manifest_data = load_manifest(root)
        checks["last_indexed_commit"] = manifest_data.last_indexed_commit
        checks["indexed_at"] = manifest_data.indexed_at
        checks["tracked_files"] = len(manifest_data.files)
        checks["total_symbols"] = sum(len(e.component_ids) for e in manifest_data.files.values())

    index_md = root / cfg.wiki_dir / "INDEX.md"
    checks["wiki_index"] = index_md.exists()

    skill_md = root / ".indexer" / "skills" / "codebase.md"
    checks["skill_file"] = skill_md.exists()

    vector_dir = root / cfg.vector_store.persist_dir
    checks["vector_db"] = vector_dir.exists()

    missing_pages = []
    if manifest_data:
        from indexer.wiki import sanitize_group_label, resolve_wiki_page_path
        wiki_dir = root / cfg.wiki_dir
        for rel_path, entry in manifest_data.files.items():
            if not entry.component_ids:
                continue
            resolved = resolve_wiki_page_path(entry.wiki_page, wiki_dir)
            if not resolved:
                missing_pages.append(entry.wiki_page)
    checks["missing_wiki_pages"] = missing_pages
    checks["missing_wiki_count"] = len(missing_pages)

    stale_files = []
    if manifest_data:
        from indexer.git import all_tracked_files, is_git_repo
        from indexer.manifest import compute_hash
        from indexer.cli import _is_indexable
        all_code = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]
        stale_files = manifest_data.stale_files(root, all_code)
    checks["stale_files"] = stale_files
    checks["stale_count"] = len(stale_files)

    cache_dir = root / ".indexer" / "cache"
    checks["cache_dir"] = cache_dir.exists()

    all_ok = (
        checks["config_file"]
        and checks["manifest_file"]
        and checks["last_indexed_commit"] is not None
        and checks["wiki_index"]
        and checks["skill_file"]
        and checks["vector_db"]
        and checks["missing_wiki_count"] == 0
        and checks["stale_count"] == 0
    )
    checks["healthy"] = all_ok

    return JSONResponse(checks)


async def sync_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    skip_deep = body.get("skip_deep", True)
    branch = body.get("branch", "")

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
    loop.run_in_executor(None, _run_sync_task, task_id, name, info["root"], skip_deep, branch)

    return JSONResponse({"task_id": task_id, "name": name, "status": "pending"})


async def rebuild_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    skip_deep = body.get("skip_deep", True)
    confirm = body.get("confirm", "")
    branch = body.get("branch", "")

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    if confirm != name:
        return JSONResponse({"error": f"confirmation failed: confirm field must match repo name '{name}'"}, status_code=400)

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
    loop.run_in_executor(None, _run_rebuild_task, task_id, name, info["root"], skip_deep, branch)

    return JSONResponse({"task_id": task_id, "name": name, "status": "pending"})


def _run_all_branches(name: str, branches: list[str], task_id: str, run_fn, **fn_kwargs):
    lock = _get_repo_lock(name)
    if not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        for br in branches:
            current = tasks.get(task_id)
            if current and current.get("status") == "failed":
                break
            run_fn(task_id, name, **fn_kwargs, branch=br, _skip_lock=True)
    finally:
        lock.release()


async def sync_all_branches(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    skip_deep = body.get("skip_deep", True)

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    # Re-discover branches if branch_rule is set
    branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")
    if branch_rule and info.get("url"):
        discovered = _discover_remote_branches(info["url"], branch_rule)
        if discovered:
            branches = discovered
            registry.register(name, info["root"], url=info.get("url", ""), branches=branches, branch_rule=branch_rule)

    if not branches:
        return JSONResponse({"error": f"no branches to sync for '{name}'"}, status_code=400)

    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: _run_all_branches(name, branches, task_id, _run_sync_task, root=info["root"], skip_deep=skip_deep))

    return JSONResponse({"task_id": task_id, "name": name, "branches": branches, "status": "pending"})


async def reindex_repo(request: Request) -> JSONResponse:
    """Atomically update repo meta + re-discover branches + rebuild all."""
    repo_name = request.path_params.get("name", "")
    info = registry.get(repo_name)
    if not info:
        return JSONResponse({"error": f"repo '{repo_name}' not registered"}, status_code=404)

    body = await _parse_body(request)
    description = body.get("description")
    tags = body.get("tags")
    branch_rule = body.get("branch_rule")
    skip_deep = body.get("skip_deep", True)

    if description is None and tags is None and branch_rule is None:
        return JSONResponse({"error": "no fields to update (send description, tags, and/or branch_rule)"}, status_code=400)

    # 1. Update meta
    registry.update_meta(repo_name, description=description, tags=tags, branch_rule=branch_rule)

    # 2. Re-discover branches if branch_rule changed
    url = info.get("url", "")
    if branch_rule is not None and url:
        discovered = _discover_remote_branches(url, branch_rule)
        if discovered:
            registry.register(repo_name, info["root"], url=url, branches=discovered, branch_rule=branch_rule, description=description, tags=tags)
        else:
            logger.warning("No branches matched branch_rule '%s' for repo %s", branch_rule, repo_name)

    # 3. Rebuild all branches
    updated_info = registry.get(repo_name)
    branches_to_rebuild = updated_info.get("branches", []) if updated_info else []
    if not branches_to_rebuild:
        return JSONResponse({"error": f"no branches to rebuild for '{repo_name}'"}, status_code=400)

    task_id = tasks.create(repo_name, url)

    def _run_all():
        lock = _get_repo_lock(repo_name)
        if not lock.acquire(blocking=False):
            tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
            return
        try:
            for br in branches_to_rebuild:
                _run_rebuild_task_inner(task_id, repo_name, updated_info["root"], skip_deep, branch=br, repo_url=url, repo_branches=branches_to_rebuild)
        finally:
            lock.release()

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_all)

    return JSONResponse({
        "task_id": task_id,
        "name": repo_name,
        "branches": branches_to_rebuild,
        "status": "pending",
    })


async def rebuild_all_branches(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    name = body.get("name", "")
    skip_deep = body.get("skip_deep", True)
    confirm = body.get("confirm", "")

    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    if confirm != name:
        return JSONResponse({"error": f"confirmation failed: confirm field must match repo name '{name}'"}, status_code=400)

    info = registry.get(name)
    if not info:
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    # Re-discover branches if branch_rule is set
    branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")
    if branch_rule and info.get("url"):
        discovered = _discover_remote_branches(info["url"], branch_rule)
        if discovered:
            branches = discovered
            registry.register(name, info["root"], url=info.get("url", ""), branches=branches, branch_rule=branch_rule)

    if not branches:
        return JSONResponse({"error": f"no branches to rebuild for '{name}'"}, status_code=400)

    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: _run_all_branches(name, branches, task_id, _run_rebuild_task, root=info["root"], skip_deep=skip_deep))

    return JSONResponse({"task_id": task_id, "name": name, "branches": branches, "status": "pending"})


def _run_indexing_pipeline(
    task_id: str,
    name: str,
    root: Path,
    skip_deep: bool,
    candidates: list[str],
    cfg: Config,
    manifest: Manifest,
    branch: str = "",
    progress_offset: int = 0,
) -> int:
    from indexer.git import all_tracked_files, is_git_repo
    total_files = len(candidates)
    tasks.update(task_id, status="running", progress=progress_offset + 20, step="parsing", detail=f"0/{total_files} files")

    all_nodes = parse_candidates(root, candidates, cfg, use_cache=True,
        progress_callback=lambda i, t, p, **kw: tasks.update(
            task_id, status="running",
            progress=progress_offset + 20 + int((i / t) * 20),
            step="parsing",
            detail=f"{i}/{t} — {p}",
        ),
    )

    if not all_nodes:
        return 0

    total_symbols = len(all_nodes)
    tasks.update(task_id, status="running", progress=progress_offset + 40, step="cross_ref", detail=f"{total_symbols} symbols")

    existing_nodes = load_existing_nodes(root, manifest, cfg)
    candidate_set = set(candidates)
    existing_nodes = [n for n in existing_nodes if n.file not in candidate_set]
    pre_cross_called_by = {n.id: list(n.called_by) for n in existing_nodes + all_nodes}
    cross_reference(existing_nodes + all_nodes)
    from indexer.indexing import _collect_affected_files
    affected_files = _collect_affected_files(set(candidates), existing_nodes + all_nodes, pre_cross_called_by)

    tasks.update(task_id, status="running", progress=progress_offset + 45, step="describing_symbols", detail="batches (concurrent)")
    from indexer.indexing import prepare_descriptions
    from indexer.llm import deep_enrich_pages, deep_enrich_index

    descriptions, file_descriptions = prepare_descriptions(root, all_nodes, existing_nodes, manifest, cfg)

    tasks.update(task_id, status="running", progress=progress_offset + 65, step="writing_wiki")
    page_enrichments: dict[str, dict] = {}
    all_manifest_files = list(set(manifest.files.keys()) | set(candidates)) if manifest.files else candidates
    groups = density_group(all_manifest_files, merge_threshold=cfg.merge_threshold)
    all_nodes_for_wiki = existing_nodes + all_nodes
    if not skip_deep:
        tasks.update(task_id, status="running", progress=progress_offset + 70, step="deep_enrichment")
        group_nodes: dict[str, list] = {}
        for node in all_nodes_for_wiki:
            group = groups.get(node.file, node.file)
            group_nodes.setdefault(group, []).append(node)
        affected_group_labels = {groups.get(f, f) for f in affected_files} if affected_files else set(groups.values())
        pages_args = [
            (group_label, list({n.file for n in nodes}), nodes, descriptions)
            for group_label, nodes in group_nodes.items()
            if group_label in affected_group_labels
        ]
        page_enrichments = deep_enrich_pages(pages_args, cfg)

    index_entries, groups = write_wiki_pages(
        root, cfg, candidates, all_nodes_for_wiki, descriptions, file_descriptions,
        page_enrichments, skip_deep, precomputed_groups=groups,
        all_files=all_manifest_files, affected_files=affected_files,
    )

    index_overview = ""
    index_flows: list[str] = []
    if not skip_deep:
        skill_pages_for_deep = [
            {"label": e.path.split("/")[-1].replace(".md", ""), "covers": e.covers, "entry_points": e.entry_points}
            for e in index_entries
        ]
        idx_enrichment = deep_enrich_index(skill_pages_for_deep, cfg)
        index_overview = idx_enrichment.get("overview", "")
        index_flows = idx_enrichment.get("flows", [])

    write_index_and_skill(
        root, cfg, index_entries, page_enrichments,
        index_overview, index_flows, total_symbols, len(candidates),
    )

    removed = manifest.removed_files(root, all_tracked_files(root) if is_git_repo(root) else [])
    tasks.update(task_id, status="running", progress=progress_offset + 85, step="embedding", detail=f"{total_symbols} symbols")
    existing_nids = {n.id for n in existing_nodes}
    upsert_vectors(root, cfg, manifest, all_nodes, descriptions, removed_files=removed, branch=branch, existing_node_ids=existing_nids)
    update_manifest(root, cfg, manifest, candidates, all_nodes, groups)

    return total_symbols


def _run_rebuild_task(task_id: str, name: str, root: Path, skip_deep: bool, branch: str = "", _skip_lock: bool = False) -> None:
    lock = _get_repo_lock(name)
    if not _skip_lock and not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    repo_url = ""
    try:
        existing = registry.get(name)
        repo_url = existing.get("url", "") if existing else ""
        repo_branches = existing.get("branches", []) if existing else []
        _run_rebuild_task_inner(task_id, name, root, skip_deep, branch=branch, repo_url=repo_url, repo_branches=repo_branches)
    finally:
        if not _skip_lock:
            lock.release()


def _run_rebuild_task_inner(task_id: str, name: str, root: Path, skip_deep: bool, branch: str = "", repo_url: str = "", repo_branches: list[str] | None = None) -> None:
    repo_branch = branch or (repo_branches[0] if repo_branches else "")

    try:
        tasks.update(task_id, status="running", progress=5, step="rebuild_init")
        from indexer.config import Config, load_config, save_config
        from indexer.manifest import Manifest, save_manifest, compute_hash, FileEntry
        from indexer.git import all_tracked_files, current_commit, is_git_repo
        from indexer.hooks import install_hook
        from indexer.cli import _is_indexable
        from indexer.grouper import density_group

        if repo_branch and is_git_repo(root):
            try:
                git_fetch_checkout_pull(root, repo_branch)
            except GitOperationError as e:
                tasks.update(task_id, status="failed", progress=15, step=f"git_{e.step}", error=e.stderr)
                return

        tasks.update(task_id, status="running", progress=10, step="cleaning")
        wiki_dir = root / "wiki"
        indexer_dir = root / ".indexer"
        if wiki_dir.exists():
            shutil.rmtree(wiki_dir)
        cache_dir = indexer_dir / "cache"
        vector_dir = indexer_dir / "vector_db"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        if vector_dir.exists():
            try:
                from indexer.vector_store import evict_client
                evict_client(str(vector_dir))
            except Exception as e:
                logger.debug("evict_client failed during rebuild: %s", e)
            shutil.rmtree(vector_dir)
        manifest_file = indexer_dir / "manifest.json"
        if manifest_file.exists():
            manifest_file.unlink()

        cfg = load_config(root)
        save_config(root, cfg)

        if is_git_repo(root) and cfg.pre_commit:
            install_hook(root, skip_deep=not cfg.deep_hook)

        tasks.update(task_id, status="running", progress=15, step="detecting_files")
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]
        candidates = all_files

        logger.info("Rebuild repo=%s branch=%s files=%d", name, repo_branch or "(default)", len(candidates))

        if not candidates:
            tasks.update(task_id, status="completed", progress=100, step="complete", detail="Nothing to index")
            return

        manifest = Manifest(last_indexed_commit=None, indexed_at="")
        total_symbols = _run_indexing_pipeline(task_id, name, root, skip_deep, candidates, cfg, manifest, branch=repo_branch)

        if total_symbols == 0:
            tasks.update(task_id, status="completed", progress=100, step="complete", detail="No symbols found")
            registry.register(name, root, url=repo_url, branches=repo_branches)
            return

        registry.register(name, root, url=repo_url, branches=repo_branches)
        info = registry.get(name)
        if not info:
            tasks.update(task_id, status="failed", error="repo was unregistered during task")
            return
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())
        webhook_url = _get_webhook_url(name)

        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name, "path": str(root),
            "has_vector_db": (root / info["config"].vector_store.persist_dir).exists(),
            "symbol_count": symbol_count, "rebuilt": True,
            "webhook_url": webhook_url,
        })
    except subprocess.TimeoutExpired as e:
        tasks.update(task_id, status="failed", progress=0, step="git_timeout", error=f"git operation timed out: {e.cmd}")
    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=_sanitize_error(str(e), repo_url, "", "", ""))



def _run_sync_task(task_id: str, name: str, root: Path, skip_deep: bool, branch: str = "", _skip_lock: bool = False) -> None:
    logger.info("Sync task started: repo=%s branch=%s", name, branch or "(any)")
    lock = _get_repo_lock(name)
    if not _skip_lock and not lock.acquire(blocking=False):
        logger.warning("Sync task skipped: repo=%s lock held by another operation", name)
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return

    repo_url = ""
    try:
        existing = registry.get(name)
        repo_url = existing.get("url", "") if existing else ""
        repo_branches = existing.get("branches", []) if existing else []
        repo_branch = branch or (repo_branches[0] if repo_branches else "")

        from indexer.git import is_git_repo, all_tracked_files, current_commit, changed_files_since

        tasks.update(task_id, status="running", progress=10, step="git_pull")
        try:
            git_fetch_checkout_pull(root, repo_branch if (repo_branch and is_git_repo(root)) else "")
        except GitOperationError as e:
            tasks.update(task_id, status="failed", progress=10, step=f"git_{e.step}", error=e.stderr)
            return

        from indexer.config import Config, load_config, save_config
        from indexer.manifest import load_manifest, save_manifest, compute_hash, FileEntry
        from indexer.cli import _is_indexable
        from indexer.grouper import density_group
        from indexer.wiki import resolve_wiki_page_path, sanitize_group_label

        cfg = load_config(root)
        if not (root / ".indexer.toml").exists():
            save_config(root, cfg)

        manifest = load_manifest(root)

        tasks.update(task_id, status="running", progress=35, step="detecting_files")
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]

        if manifest.last_indexed_commit is None:
            candidates = list(all_files)
        else:
            git_changed = changed_files_since(root, manifest.last_indexed_commit) if is_git_repo(root) else []
            stale = manifest.stale_files(root, all_files)
            candidates = list(set(git_changed + stale))

        wiki_dir = root / cfg.wiki_dir

        missing_wiki = []
        for rel_path, entry in manifest.files.items():
            if not entry.component_ids:
                continue
            resolved = resolve_wiki_page_path(entry.wiki_page, wiki_dir)
            if not resolved and rel_path not in candidates:
                missing_wiki.append(rel_path)
        if missing_wiki:
            candidates.extend(missing_wiki)

        vector_dir = root / cfg.vector_store.persist_dir
        if not vector_dir.exists() and all_files:
            for f in all_files:
                if f not in candidates:
                    candidates.append(f)

        wiki_index_missing = not (root / cfg.wiki_dir / "INDEX.md").exists()
        skill_missing = not (root / ".indexer" / "skills" / "codebase.md").exists()

        candidates = [f for f in candidates if _is_indexable(f, cfg)]

        logger.info("Sync repo=%s branch=%s candidates=%d missing_wiki=%d", name, repo_branch or "(default)", len(candidates), len(missing_wiki))

        need_regen_meta = (wiki_index_missing or skill_missing) and not candidates

        if not candidates and not need_regen_meta:
            tasks.update(task_id, status="completed", progress=100, step="complete", detail="Nothing to sync")
            return

        if need_regen_meta and not candidates:
            tasks.update(task_id, status="running", progress=40, step="writing_wiki", detail="Repairing missing meta files")
            wiki_dir = root / cfg.wiki_dir
            wiki_dir.mkdir(parents=True, exist_ok=True)
            index_entries = []
            for rel_path, entry in manifest.files.items():
                if entry.wiki_page.startswith(cfg.wiki_dir + "/"):
                    raw_label = entry.wiki_page[len(cfg.wiki_dir) + 1:].removesuffix(".md")
                    safe_name = sanitize_group_label(raw_label)
                    actual_path = f"{cfg.wiki_dir}/{safe_name}.md"
                else:
                    actual_path = entry.wiki_page
                wiki_path = root / actual_path
                if wiki_path.exists():
                    from indexer.wiki import IndexEntry
                    index_entries.append(IndexEntry(
                        path=str(wiki_path.relative_to(root)),
                        covers=rel_path,
                        entry_points=entry.component_ids[:5] if entry.component_ids else [],
                    ))
            commit = current_commit(root) or manifest.last_indexed_commit or "unknown"
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if wiki_index_missing:
                from indexer.wiki import build_index, write_index
                index_content = build_index(index_entries, commit, today)
                write_index(wiki_dir, index_content)
            if skill_missing:
                sym_count = sum(len(entry.component_ids) for entry in manifest.files.values())
                write_index_and_skill(root, cfg, index_entries, {}, "", [], sym_count, len(manifest.files))
            webhook_url = _get_webhook_url(name)
            registry.register(name, root, url=repo_url, branches=repo_branches)
            tasks.update(task_id, status="completed", progress=100, step="complete", result={
                "name": name, "path": str(root),
                "has_vector_db": (root / cfg.vector_store.persist_dir).exists(),
                "symbol_count": sum(len(e.component_ids) for e in manifest.files.values()),
                "synced": True, "repaired": True,
                "webhook_url": webhook_url,
            })
            return

        total_symbols = _run_indexing_pipeline(task_id, name, root, skip_deep, candidates, cfg, manifest, branch=repo_branch)

        webhook_url = _get_webhook_url(name)
        registry.register(name, root, url=repo_url, branches=repo_branches)
        info = registry.get(name)
        if not info:
            tasks.update(task_id, status="failed", error="repo was unregistered during task")
            return
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())

        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name, "path": str(root),
            "has_vector_db": (root / info["config"].vector_store.persist_dir).exists(),
            "symbol_count": symbol_count, "synced": True,
            "webhook_url": webhook_url,
        })

    except subprocess.TimeoutExpired as e:
        tasks.update(task_id, status="failed", progress=10, step="git_timeout", error=f"git operation timed out: {e.cmd}")
    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=_sanitize_error(str(e), repo_url, "", "", ""))
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
    skip_deep: bool,
    force_reindex: bool,
    branch_rule: str = "",
) -> None:
    lock = _get_repo_lock(name)
    if not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        _run_register_task_inner(task_id, name, url, username, password, token, branch, skip_deep, force_reindex, branch_rule)
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
    skip_deep: bool,
    force_reindex: bool,
    branch_rule: str = "",
) -> None:
    clone_url = _inject_credentials(url, username, password, token)
    clone_dir = registry.repos_dir / name

    from indexer.git import _GIT_ENV
    git_env = _GIT_ENV
    git_cfg = ["-c", "http.followRedirects=true"]

    try:
        if clone_dir.exists() and (clone_dir / ".git").exists():
            tasks.update(task_id, status="running", progress=10, step="git_pull")
            try:
                git_fetch_checkout_pull(
                    clone_dir, branch,
                    sanitize_fn=lambda s: _sanitize_error(s, url, username, password, token),
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

        from indexer.config import Config, load_config, save_config
        from indexer.manifest import load_manifest, Manifest
        from indexer.git import all_tracked_files, current_commit, is_git_repo, changed_files_since
        from indexer.cli import _is_indexable, _ensure_cache_gitignore
        from indexer.hooks import install_hook

        root = clone_dir

        detected_branch = _detect_default_branch(clone_dir) if is_git_repo(clone_dir) else ""
        if detected_branch and not branch:
            branch = detected_branch

        if detected_branch:
            registry.register(name, clone_dir, url=url, branches=[detected_branch], branch_rule=branch_rule)

        tasks.update(task_id, status="running", progress=30, step="init")
        cfg = load_config(root)
        save_config(root, cfg)
        _ensure_cache_gitignore(root, verbose=False)
        if is_git_repo(root) and cfg.pre_commit:
            install_hook(root, skip_deep=not cfg.deep_hook)

        tasks.update(task_id, status="running", progress=35, step="detecting_files")
        manifest = load_manifest(root)
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]

        # If branch_rule is set, discover and register all matching branches
        if branch_rule and url:
            discovered = _discover_remote_branches(url, branch_rule)
            if discovered:
                registry.register(name, clone_dir, url=url, branches=discovered, branch_rule=branch_rule)
            else:
                logger.warning("No branches matched branch_rule '%s' for repo %s", branch_rule, name)

        # Determine which branches to index
        repo_info = registry.get(name)
        registered_branches = repo_info.get("branches", []) if repo_info else ([] if not branch else [branch])
        branches_to_index = registered_branches if branch_rule else ([branch] if branch else registered_branches[:1])

        if not branches_to_index:
            tasks.update(task_id, status="completed", progress=100, step="complete", result={
                "name": name, "path": str(clone_dir), "indexed": False, "warning": "No branches to index",
            })
            return

        for idx, current_branch in enumerate(branches_to_index):
            if not current_branch:
                continue

            tasks.update(task_id, status="running", progress=40 + (50 * idx // len(branches_to_index)),
                         step=f"checkout_{current_branch}")

            # Checkout the branch
            r = subprocess.run(
                ["git"] + git_cfg + ["checkout", current_branch],
                cwd=root, capture_output=True, text=True, timeout=30, env=git_env,
            )
            if r.returncode != 0:
                tasks.update(task_id, status="failed", progress=40, step=f"checkout_{current_branch}", error=_sanitize_error(r.stderr, url, username, password, token))
                return
            r = subprocess.run(
                ["git"] + git_cfg + ["pull", "--rebase", "origin", current_branch],
                cwd=root, capture_output=True, text=True, timeout=60, env=git_env,
            )
            if r.returncode != 0:
                tasks.update(task_id, status="failed", progress=40, step=f"pull_{current_branch}", error=_sanitize_error(r.stderr, url, username, password, token))
                return

            # Index this branch
            manifest = load_manifest(root)
            all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]
            if manifest.last_indexed_commit is None:
                candidates = all_files
            else:
                git_changed = changed_files_since(root, manifest.last_indexed_commit) if is_git_repo(root) else []
                stale = manifest.stale_files(root, all_files)
                candidates = list(set(git_changed + stale))
            candidates = [f for f in candidates if _is_indexable(f, cfg)]

            logger.info("Register repo=%s branch=%s candidates=%d all_files=%d", name, current_branch, len(candidates), len(all_files))

            _run_indexing_pipeline(task_id, name, root, skip_deep, candidates, cfg, manifest, branch=current_branch, progress_offset=40 + (50 * idx // len(branches_to_index)))

        webhook_url = _get_webhook_url(name)
        info = registry.get(name)
        if not info:
            tasks.update(task_id, status="failed", error="repo was unregistered during task")
            return
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())

        tasks.update(task_id, status="completed", progress=100, step="complete", result={
            "name": name,
            "path": str(clone_dir),
            "url": url,
            "has_vector_db": (clone_dir / info["config"].vector_store.persist_dir).exists(),
            "symbol_count": symbol_count,
            "indexed": True,
            "webhook_url": webhook_url,
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
    try:
        top_k = max(1, min(int(body.get("top_k", 10)), 100))
        expand_depth = max(1, min(int(body.get("expand_depth", 1)), 5))
    except (ValueError, TypeError):
        return JSONResponse({"error": "top_k and expand_depth must be integers"}, status_code=400)
    rewrite = body.get("rewrite", True)

    if not query:
        return JSONResponse({"error": "query is required"}, status_code=400)

    queries = [query]
    targets = _resolve_repos(repo)
    if not targets:
        return JSONResponse({"error": "no repos available"}, status_code=404)

    if rewrite:
        any_repo = next(iter(targets), None)
        if any_repo:
            from indexer.llm import rewrite_query
            queries = rewrite_query(query, any_repo[1]["config"])

    from collections import defaultdict
    by_emb: dict[tuple, list[tuple[str, dict]]] = defaultdict(list)
    for name, info in targets:
        cfg = info["config"]
        key = (cfg.embedding.provider, cfg.embedding.dimensions)
        by_emb[key].append((name, info))

    all_hits = []
    seen_ids: set[str] = set()

    for emb_key, group in by_emb.items():
        emb_cfg = group[0][1]["config"].embedding
        all_query_vectors = [embed_query(q, emb_cfg) for q in queries]

        for name, info in group:
            cfg = info["config"]
            root = info["root"]
            repo_branches = info.get("branches", [])
            if len(repo_branches) > 1:
                branch_conditions = [{"branch": b} for b in repo_branches]
                where_clause = {"$or": branch_conditions} if branch_conditions else None
            elif len(repo_branches) == 1:
                where_clause = {"branch": repo_branches[0]}
            else:
                where_clause = None
            for qv in all_query_vectors:
                hits = search(qv, cfg.vector_store, root, top_k=top_k * 2, where=where_clause)
                for h in hits:
                    h["repo"] = name
                    if h["id"] not in seen_ids:
                        seen_ids.add(h["id"])
                        all_hits.append(h)

    truncate_documents(all_hits)

    all_hits.sort(key=lambda h: h.get("distance", 1.0))
    all_hits = all_hits[:top_k]

    if expand_depth > 0:
        expanded = []
        expanded_ids: set[str] = set()
        for name, info in targets:
            cfg = info["config"]
            root = info["root"]
            repo_hits = [h for h in all_hits if h.get("repo") == name]
            expanded_hits = _expand_with_call_graph(repo_hits, cfg, root, name, expand_depth)
            truncate_documents(expanded_hits)
            for h in expanded_hits:
                if h["id"] not in expanded_ids:
                    expanded_ids.add(h["id"])
                    expanded.append(h)
        all_hits = expanded

    all_hits.sort(key=lambda h: h.get("distance", 1.0))
    all_hits = all_hits[:top_k]

    return JSONResponse({
        "results": all_hits,
        "total": len(all_hits),
        "rewritten_queries": queries if len(queries) > 1 else None,
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

    if not symbol_id:
        return JSONResponse({"error": "symbol_id is required"}, status_code=400)

    all_nodes = []
    targets = _resolve_repos(repo)

    for name, info in targets:
        cfg = info["config"]
        root = info["root"]
        nodes = _trace_call_impl(symbol_id, cfg, root, direction, max_depth)
        for n in nodes:
            n["repo"] = name
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


async def list_repos(request: Request) -> JSONResponse:
    from indexer.manifest import load_manifest
    result = []
    for name in registry.list_names():
        info = registry.get(name)
        if not info:
            continue
        root = info["root"]
        has_vectors = (root / info["config"].vector_store.persist_dir).exists()
        manifest_path = root / ".indexer" / "manifest.json"
        symbol_count = 0
        last_synced_at = ""
        last_indexed_commit = ""
        if manifest_path.exists():
            manifest = load_manifest(root)
            symbol_count = sum(len(entry.component_ids) for entry in manifest.files.values())
            last_synced_at = manifest.indexed_at or ""
            if manifest.last_indexed_commit:
                last_indexed_commit = manifest.last_indexed_commit[:7]
        if not last_synced_at:
            try:
                from indexer.git import current_commit, _GIT_ENV
                commit = current_commit(root)
                if commit:
                    out = subprocess.run(
                        ["git", "log", "-1", "--format=%cI", commit],
                        cwd=root, capture_output=True, text=True, timeout=10, env=_GIT_ENV,
                    )
                    if out.returncode == 0 and out.stdout.strip():
                        last_synced_at = out.stdout.strip()
            except Exception:
                pass
        branches = info.get("branches", [])
        webhook_url = _get_webhook_url(name, request)
        result.append({
            "name": name,
            "path": str(root),
            "url": info.get("url", ""),
            "branches": branches,
            "description": info.get("description", ""),
            "tags": info.get("tags", []),
            "webhook_url": webhook_url,
            "has_vector_db": has_vectors,
            "symbol_count": symbol_count,
            "last_synced_at": last_synced_at,
            "last_indexed_commit": last_indexed_commit,
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
    manifest_path = root / ".indexer" / "manifest.json"
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

    manifest_data = {}
    if manifest_path.exists():
        from indexer.manifest import load_manifest
        manifest = load_manifest(root)
        manifest_data = {
            "last_indexed_commit": manifest.last_indexed_commit,
            "indexed_at": manifest.indexed_at,
            "files": {
                k: {
                    "hash": v.hash,
                    "wiki_page": v.wiki_page,
                    "component_ids": v.component_ids,
                }
                for k, v in manifest.files.items()
            },
        }

    skill_content = ""
    if skill_path.exists():
        skill_content = skill_path.read_text(encoding="utf-8", errors="replace")

    webhook_url = _get_webhook_url(repo_name, request)

    # Gather per-branch detail: commit hash + index status
    branches = info.get("branches", [])
    branch_rule = info.get("branch_rule", "")
    branches_detail = []
    branches_missing = []

    # If branch_rule is set, discover what's on remote vs what's registered
    if branch_rule and info.get("url"):
        try:
            discovered = _discover_remote_branches(info["url"], branch_rule)
            registered_set = set(branches)
            for br in discovered:
                if br not in registered_set:
                    branches_missing.append({"name": br, "commit": ""})
            # Also get commit for missing branches
            is_git = (root / ".git").exists()
            if is_git:
                for br in branches_missing:
                    try:
                        from indexer.git import _GIT_ENV as _git_env_ls
                        r = subprocess.run(
                            ["git", "ls-remote", info["url"], f"refs/heads/{br['name']}"],
                            capture_output=True, text=True, timeout=15, env=_git_env_ls,
                        )
                        if r.returncode == 0 and r.stdout.strip():
                            br["commit"] = r.stdout.strip().split("\t")[0]
                    except Exception:
                        pass
        except Exception as e:
            logger.warning("Failed to discover branches for %s: %s", repo_name, e)

    is_git = (root / ".git").exists()
    # Pre-setup vector store client for branch status checks
    vector_collection = None
    persist_dir_path = root / cfg.vector_store.persist_dir
    has_vector_files = False
    if persist_dir_path.exists():
        has_vector_files = any(
            f.suffix in (".sqlite3", ".bin", ".pkl") or
            (f.is_dir() and f.name.startswith("chroma"))
            for f in persist_dir_path.iterdir()
        )
        if not has_vector_files:
            has_vector_files = len(list(persist_dir_path.iterdir())) > 0

    try:
        from indexer.vector_store import _get_client
        if persist_dir_path.exists():
            vector_client = _get_client(str(persist_dir_path))
            try:
                vector_collection = vector_client.get_collection(cfg.vector_store.collection_name)
            except Exception:
                vector_collection = None
    except Exception:
        pass

    for b in branches:
        commit_hash = ""
        if is_git:
            try:
                from indexer.git import _GIT_ENV as _git_env_detail
                r = subprocess.run(
                    ["git", "rev-parse", "refs/remotes/origin/" + b],
                    cwd=root, capture_output=True, text=True, timeout=10, env=_git_env_detail,
                )
                if r.returncode == 0:
                    commit_hash = r.stdout.strip()
            except Exception:
                pass

        # Check vector store for this branch
        has_branch_vectors = False
        if vector_collection is not None:
            try:
                total_count = vector_collection.count()
                if total_count > 0:
                    # Try exact branch match
                    branch_chunk = vector_collection.get(
                        where={"branch": b}, limit=1, include=["metadatas"],
                    )
                    has_branch_vectors = bool(branch_chunk and branch_chunk.get("ids"))
                    # Fallback: if no branch metadata found, check if this is old-style
                    # data (no branch field in any vector). If so, treat as indexed
                    # since the data IS there, just without branch discrimination.
                    if not has_branch_vectors:
                        any_sample = vector_collection.get(limit=1, include=["metadatas"])
                        if any_sample and any_sample.get("metadatas"):
                            first_meta = any_sample["metadatas"][0]
                            if "branch" not in first_meta or not first_meta["branch"]:
                                has_branch_vectors = True
            except Exception:
                pass
        # Fallback: if chroma failed but vector files exist on disk, trust the filesystem
        if not has_branch_vectors and has_vector_files:
            has_branch_vectors = True

        branches_detail.append({
            "name": b,
            "commit": commit_hash,
            "indexed": has_branch_vectors,
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
        "manifest": manifest_data,
        "skill": skill_content,
        "has_vector_db": (root / cfg.vector_store.persist_dir).exists(),
        "last_synced_at": manifest_data.get("indexed_at", "") if manifest_data else "",
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
    from indexer.wiki import sanitize_group_label
    from indexer.config import load_config
    from indexer.manifest import load_manifest

    all_repos = []
    for name, info in registry.items():
        root = info["root"]
        cfg = info["config"]
        manifest = load_manifest(root)
        wiki_dir = root / cfg.wiki_dir
        skill_path = root / ".indexer" / "skills" / "codebase.md"

        wiki_pages = []
        if wiki_dir.exists():
            for md_file in sorted(wiki_dir.glob("*.md")):
                wiki_pages.append({
                    "name": md_file.stem,
                    "path": str(md_file.relative_to(root)),
                })

        total_symbols = sum(len(e.component_ids) for e in manifest.files.values())
        total_files = len(manifest.files)
        commit = manifest.last_indexed_commit or "unknown"
        indexed_date = manifest.indexed_at or "unknown"

        skill_content = ""
        if skill_path.exists():
            skill_content = skill_path.read_text(encoding="utf-8", errors="replace")

        all_repos.append({
            "name": name,
            "path": str(root),
            "total_symbols": total_symbols,
            "total_files": total_files,
            "commit": commit,
            "indexed_date": indexed_date,
            "wiki_pages": wiki_pages,
            "skill": skill_content,
            "has_vector_db": (root / cfg.vector_store.persist_dir).exists(),
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
            f" — indexed {r['indexed_date']} @ `{r['commit'][:8]}`"
        )
        combined_lines.append(f"- Path: `{r['path']}`")
        combined_lines.append(f"- Vector DB: {'yes' if r['has_vector_db'] else 'no'}")

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
            registry.register(name, path, url="", branches=[])

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
            Route("/register", register_repo, methods=["POST"]),
            Route("/unregister", unregister_repo, methods=["POST"]),
            Route("/sync", sync_repo, methods=["POST"]),
            Route("/sync-all", sync_all_branches, methods=["POST"]),
            Route("/rebuild", rebuild_repo, methods=["POST"]),
            Route("/rebuild-all", rebuild_all_branches, methods=["POST"]),
            Route("/webhook/{name}", webhook_by_name, methods=["POST"]),
            Route("/api/repo/{name}", repo_detail),
            Route("/api/repo/{name}", update_repo_meta, methods=["PATCH"]),
            Route("/api/repo/{name}/reindex", reindex_repo, methods=["POST"]),
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


def _trace_call_impl(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    direction: str,
    max_depth: int,
) -> list[dict]:
    return _trace_call_retrieval(symbol_id, cfg, repo_root, direction=direction, max_depth=max_depth)


def _expand_with_call_graph(
    hits: list[dict],
    cfg: Config,
    repo_root: Path,
    repo_name: str,
    depth: int = 1,
) -> list[dict]:
    expanded = _expand_retrieval(hits, cfg, repo_root, depth=depth)
    for h in expanded:
        h["repo"] = repo_name
    return expanded


class _InvalidBodyError(Exception):
    pass


async def _parse_body(request: Request) -> dict:
    try:
        body = await request.json()
    except Exception:
        raise _InvalidBodyError("invalid JSON body")
    if not isinstance(body, dict):
        raise _InvalidBodyError("request body must be a JSON object")
    return body
