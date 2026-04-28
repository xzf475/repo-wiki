# indexer/rest_api.py
from __future__ import annotations
import asyncio
import fnmatch
import json
import logging
import os
import re
import threading
import uuid
from pathlib import Path

from indexer.utils import load_env_file
try:
    load_env_file()
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

import subprocess
import tempfile
import urllib.parse
from starlette.applications import Starlette

logger = logging.getLogger(__name__)
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

from indexer.config import Config, load_config, save_config, EmbeddingConfig, VectorStoreConfig
from indexer.embedding import embed_query
from indexer.vector_store import search, get_by_ids
from indexer.indexing import (
    cross_reference, load_existing_nodes, parse_candidates,
    build_batches, write_wiki_pages, write_index_and_skill,
    update_manifest, upsert_vectors,
)
from indexer.grouper import density_group

logger = logging.getLogger("repo-wiki-api")

_repo_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_repo_lock(name: str) -> threading.Lock:
    with _locks_lock:
        if name not in _repo_locks:
            _repo_locks[name] = threading.Lock()
        return _repo_locks[name]


class TaskStore:
    _MAX_TASKS = 200
    _TTL_SECONDS = 3600

    def __init__(self):
        self.tasks: dict[str, dict] = {}

    def _cleanup(self):
        import time
        now = time.time()
        expired = [tid for tid, t in self.tasks.items()
                   if t.get("status") in ("completed", "failed")
                   and now - t.get("_finished_at", now) > self._TTL_SECONDS]
        for tid in expired:
            del self.tasks[tid]
        if len(self.tasks) > self._MAX_TASKS:
            oldest = sorted(self.tasks.items(), key=lambda x: x[1].get("_created_at", 0))
            for tid, _ in oldest[:len(self.tasks) - self._MAX_TASKS]:
                del self.tasks[tid]

    def create(self, name: str, url: str) -> str:
        import time
        self._cleanup()
        task_id = uuid.uuid4().hex[:12]
        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "url": url,
            "status": "pending",
            "progress": 0,
            "step": "queued",
            "detail": None,
            "result": None,
            "error": None,
            "_created_at": time.time(),
        }
        return task_id

    def get(self, task_id: str) -> dict | None:
        return self.tasks.get(task_id)

    def update(self, task_id: str, **kwargs):
        import time
        if task_id in self.tasks:
            if kwargs.get("status") in ("completed", "failed"):
                kwargs["_finished_at"] = time.time()
            self.tasks[task_id].update(kwargs)


tasks = TaskStore()


def _detect_default_branch(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            ref = result.stdout.strip()
            if ref.startswith("refs/remotes/origin/"):
                return ref[len("refs/remotes/origin/"):]
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "remote", "show", "origin"],
            cwd=repo_root, capture_output=True, text=True, timeout=15,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("HEAD branch:"):
                return line.split(":")[-1].strip()
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "main"


def _discover_remote_branches(url: str, pattern: str) -> list[str]:
    """Use git ls-remote to find remote branches matching a glob pattern."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        branches = []
        for line in result.stdout.splitlines():
            if "\t" not in line:
                continue
            ref = line.split("\t")[-1].strip()
            if ref.startswith("refs/heads/"):
                branch_name = ref[len("refs/heads/"):]
                if fnmatch.fnmatch(branch_name, pattern):
                    branches.append(branch_name)
        return branches
    except Exception as e:
        logger.warning("Failed to discover remote branches for %s: %s", url, e)
        return []


class RepoRegistry:
    def __init__(self, repos_dir: Path | None = None):
        self.repos: dict[str, dict] = {}
        self.repos_dir = repos_dir or Path(tempfile.gettempdir()) / "repo_wiki_repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self.repos_dir / "repos_registry.json"

    def _save(self):
        data = {
            name: {
                "root": str(info["root"]),
                "url": info.get("url", ""),
                "branches": info.get("branches", []),
                "branch_rule": info.get("branch_rule", ""),
            }
            for name, info in self.repos.items()
        }
        self._registry_file.write_text(json.dumps(data, indent=2))

    def _load(self):
        if not self._registry_file.exists():
            return
        try:
            data = json.loads(self._registry_file.read_text())
            for name, entry in data.items():
                if isinstance(entry, str):
                    path_str = entry
                    url = ""
                    branches = []
                    branch_rule = ""
                else:
                    path_str = entry.get("root", "")
                    url = entry.get("url", "")
                    branch_rule = entry.get("branch_rule", "")
                    raw = entry.get("branches", entry.get("branch", ""))
                    if isinstance(raw, str):
                        branches = [raw] if raw else []
                    else:
                        branches = raw
                repo_root = Path(path_str)
                if not branches:
                    detected = _detect_default_branch(repo_root)
                    branches = [detected] if detected else ["main"]
                if repo_root.exists():
                    cfg = load_config(repo_root)
                    self.repos[name] = {"root": repo_root, "config": cfg, "url": url, "branches": branches, "branch_rule": branch_rule}
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load repo registry: %s", e)

    def register(self, name: str, repo_root: Path, url: str = "", branches: list[str] | None = None, branch_rule: str = ""):
        cfg = load_config(repo_root)
        self.repos[name] = {
            "root": repo_root,
            "config": cfg,
            "url": url,
            "branches": branches or [],
            "branch_rule": branch_rule,
        }
        self._save()
        logger.info(f"Registered repo '{name}' at {repo_root}")

    def unregister(self, name: str):
        if name in self.repos:
            del self.repos[name]
            self._save()
            logger.info(f"Unregistered repo '{name}'")

    def get(self, name: str) -> dict | None:
        return self.repos.get(name)

    def list_names(self) -> list[str]:
        return sorted(self.repos.keys())


registry = RepoRegistry()
registry._load()


async def register_repo(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    url = body.get("url", "")
    name = body.get("name", "")
    username = body.get("username", "")
    password = body.get("password", "")
    token = body.get("token", "")
    branch = body.get("branch", "")
    branches = body.get("branches", body.get("branches", []))
    branch_rule = body.get("branch_rule", "")
    skip_deep = body.get("skip_deep", True)
    force_reindex = body.get("force_reindex", False)

    if not branches and branch:
        branches = [branch]
    if not branches:
        branches = body.get("branches", [])

    # If a branch rule is specified, discover matching branches from remote
    if branch_rule and not branches:
        discovered = _discover_remote_branches(url, branch_rule)
        if not discovered:
            return JSONResponse({"error": f"no remote branches match pattern '{branch_rule}'"}, status_code=400)
        branches = discovered

    if not url:
        return JSONResponse({"error": "url is required"}, status_code=400)

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in ("https", "git", "ssh", "http"):
        return JSONResponse({"error": "only https/git/ssh URLs allowed"}, status_code=400)

    if not name:
        repo_name = parsed_url.path.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        name = repo_name

    if not re.match(r'^[a-zA-Z0-9._-]+$', name):
        return JSONResponse({"error": "name must contain only alphanumeric, dot, hyphen, underscore"}, status_code=400)

    if registry.get(name) and not force_reindex:
        return JSONResponse({
            "error": f"repo '{name}' already registered",
            "existing": str(registry.get(name)["root"]),
        }, status_code=409)

    task_id = tasks.create(name, url)

    clone_dir = registry.repos_dir / name
    clone_dir.mkdir(parents=True, exist_ok=True)
    branches_list = [branch] if branch else branches or ["main"]
    registry.register(name, clone_dir, url=url, branches=branches_list, branch_rule=branch_rule)

    webhook_url = _get_webhook_url(name)

    # Use the first branch for initial clone, but register all branches
    first_branch = branches_list[0] if branches_list else ""

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
    return JSONResponse(task)


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
        from indexer.wiki import sanitize_group_label
        for rel_path, entry in manifest_data.files.items():
            if not entry.component_ids:
                continue
            if entry.wiki_page.startswith(cfg.wiki_dir + "/"):
                raw_label = entry.wiki_page[len(cfg.wiki_dir) + 1:].removesuffix(".md")
                safe_name = sanitize_group_label(raw_label)
                actual_path = f"{cfg.wiki_dir}/{safe_name}.md"
            else:
                actual_path = entry.wiki_page
            wiki_path = root / actual_path
            if not wiki_path.exists():
                missing_pages.append(actual_path)
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

    task_id = tasks.create(name, info.get("url", ""))

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_rebuild_task, task_id, name, info["root"], skip_deep, branch)

    return JSONResponse({"task_id": task_id, "name": name, "status": "pending"})


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

    if len(branches) < 1:
        return JSONResponse({"error": f"no branches to sync for '{name}'"}, status_code=400)

    task_id = tasks.create(name, info.get("url", ""))

    def _run_all():
        for br in branches:
            _run_sync_task(task_id, name, info["root"], skip_deep, branch=br)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_all)

    return JSONResponse({"task_id": task_id, "name": name, "branches": branches, "status": "pending"})


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

    if len(branches) < 1:
        return JSONResponse({"error": f"no branches to rebuild for '{name}'"}, status_code=400)

    task_id = tasks.create(name, info.get("url", ""))

    def _run_all():
        for br in branches:
            _run_rebuild_task(task_id, name, info["root"], skip_deep, branch=br)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_all)

    return JSONResponse({"task_id": task_id, "name": name, "branches": branches, "status": "pending"})


def _run_indexing_pipeline(
    task_id: str,
    name: str,
    root: Path,
    skip_deep: bool,
    candidates: list[str],
    cfg: Config,
    manifest,
    branch: str = "",
) -> int:
    from indexer.git import all_tracked_files, is_git_repo
    total_files = len(candidates)
    tasks.update(task_id, status="running", progress=20, step="parsing", detail=f"0/{total_files} files")

    all_nodes = parse_candidates(root, candidates, cfg, use_cache=True,
        progress_callback=lambda i, t, p, **kw: tasks.update(
            task_id, status="running",
            progress=20 + int((i / t) * 20),
            step="parsing",
            detail=f"{i}/{t} — {p}",
        ),
    )

    if not all_nodes:
        return 0

    total_symbols = len(all_nodes)
    tasks.update(task_id, status="running", progress=40, step="cross_ref", detail=f"{total_symbols} symbols")

    existing_nodes = load_existing_nodes(root, manifest, cfg)
    cross_reference(existing_nodes + all_nodes)

    tasks.update(task_id, status="running", progress=45, step="describing_symbols", detail="batches (concurrent)")
    batches = build_batches(all_nodes, cfg)
    from indexer.llm import describe_nodes, describe_files, deep_enrich_pages, deep_enrich_index
    descriptions = describe_nodes(batches, cfg)

    tasks.update(task_id, status="running", progress=58, step="describing_modules")
    file_nodes: dict[str, list] = {}
    for node in all_nodes:
        file_nodes.setdefault(node.file, []).append(node)
    file_descriptions = describe_files(file_nodes, cfg)

    tasks.update(task_id, status="running", progress=65, step="writing_wiki")
    page_enrichments: dict[str, dict] = {}
    if not skip_deep:
        tasks.update(task_id, status="running", progress=70, step="deep_enrichment")
        groups = density_group(candidates, merge_threshold=cfg.merge_threshold)
        group_nodes: dict[str, list] = {}
        for node in all_nodes:
            group = groups.get(node.file, node.file)
            group_nodes.setdefault(group, []).append(node)
        pages_args = [
            (group_label, list({n.file for n in nodes}), nodes, descriptions)
            for group_label, nodes in group_nodes.items()
        ]
        page_enrichments = deep_enrich_pages(pages_args, cfg)

    index_entries, groups = write_wiki_pages(
        root, cfg, candidates, all_nodes, descriptions, file_descriptions,
        page_enrichments, skip_deep,
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
    update_manifest(root, cfg, manifest, candidates, all_nodes, groups)

    tasks.update(task_id, status="running", progress=85, step="embedding", detail=f"{total_symbols} symbols")
    upsert_vectors(root, cfg, manifest, all_nodes, descriptions, removed_files=removed, branch=branch)

    return total_symbols


def _run_rebuild_task(task_id: str, name: str, root: Path, skip_deep: bool, branch: str = "") -> None:
    lock = _get_repo_lock(name)
    if not lock.acquire(blocking=False):
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    try:
        existing = registry.get(name)
        repo_url = existing.get("url", "") if existing else ""
        repo_branches = existing.get("branches", []) if existing else []
        repo_branch = branch or (repo_branches[0] if repo_branches else "")

        import shutil

        tasks.update(task_id, status="running", progress=5, step="cleaning")
        wiki_dir = root / "wiki"
        indexer_dir = root / ".indexer"
        if wiki_dir.exists():
            shutil.rmtree(wiki_dir)
        cache_dir = indexer_dir / "cache"
        vector_dir = indexer_dir / "vector_db"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        if vector_dir.exists():
            shutil.rmtree(vector_dir)
        manifest_file = indexer_dir / "manifest.json"
        if manifest_file.exists():
            manifest_file.unlink()

        tasks.update(task_id, status="running", progress=10, step="rebuild_init")
        from indexer.config import Config, load_config, save_config
        from indexer.manifest import Manifest, save_manifest, compute_hash, FileEntry
        from indexer.git import all_tracked_files, current_commit, is_git_repo
        from indexer.hooks import install_hook
        from indexer.cli import _is_indexable
        from indexer.grouper import density_group

        if repo_branch and is_git_repo(root):
            subprocess.run(
                ["git", "checkout", repo_branch],
                cwd=root, capture_output=True, text=True, timeout=30,
            )
            subprocess.run(
                ["git", "fetch", "--all"],
                cwd=root, capture_output=True, text=True, timeout=60,
            )
            subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=root, capture_output=True, text=True, timeout=60,
            )

        cfg = load_config(root)
        save_config(root, cfg)

        logger.info("Rebuild repo=%s branch=%s files=%d", name, repo_branch or "(default)", len(candidates) if candidates else 0)
        if is_git_repo(root) and cfg.pre_commit:
            install_hook(root, skip_deep=not cfg.deep_hook)

        tasks.update(task_id, status="running", progress=15, step="detecting_files")
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]
        candidates = all_files

        if not candidates:
            tasks.update(task_id, status="done", progress=100, step="complete", detail="Nothing to index")
            return

        manifest = Manifest()
        total_symbols = _run_indexing_pipeline(task_id, name, root, skip_deep, candidates, cfg, manifest, branch=repo_branch)

        if total_symbols == 0:
            tasks.update(task_id, status="done", progress=100, step="complete", detail="No symbols found")
            registry.register(name, root, url=repo_url, branches=repo_branches)
            return

        registry.register(name, root, url=repo_url, branches=repo_branches)
        info = registry.get(name)
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())
        webhook_url = _get_webhook_url(name)

        tasks.update(task_id, status="done", progress=100, step="complete", result={
            "name": name, "path": str(root),
            "has_vector_db": (root / info["config"].vector_store.persist_dir).exists(),
            "symbol_count": symbol_count, "rebuilt": True,
            "webhook_url": webhook_url,
        })

    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=str(e))
    finally:
        lock.release()



def _run_sync_task(task_id: str, name: str, root: Path, skip_deep: bool, branch: str = "") -> None:
    logger.info("Sync task started: repo=%s branch=%s", name, branch or "(any)")
    lock = _get_repo_lock(name)
    if not lock.acquire(blocking=False):
        logger.warning("Sync task skipped: repo=%s lock held by another operation", name)
        tasks.update(task_id, status="failed", progress=0, step="locked", error="Another operation is running on this repo")
        return
    existing = registry.get(name)
    repo_url = existing.get("url", "") if existing else ""
    repo_branches = existing.get("branches", []) if existing else []
    repo_branch = branch or (repo_branches[0] if repo_branches else "")
    git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    git_cfg = ["-c", "http.followRedirects=true"]

    from indexer.git import is_git_repo, all_tracked_files, current_commit, changed_files_since

    try:
        tasks.update(task_id, status="running", progress=10, step="git_pull")
        if repo_branch and is_git_repo(root):
            subprocess.run(
                ["git"] + git_cfg + ["checkout", repo_branch],
                cwd=root, capture_output=True, text=True, timeout=30, env=git_env,
            )
        subprocess.run(
            ["git"] + git_cfg + ["fetch", "--all"],
            cwd=root, capture_output=True, text=True, timeout=60, env=git_env,
        )
        subprocess.run(
            ["git"] + git_cfg + ["pull", "--rebase"],
            cwd=root, capture_output=True, text=True, timeout=60, env=git_env,
        )

        from indexer.config import Config, load_config, save_config
        from indexer.manifest import load_manifest, save_manifest, compute_hash, FileEntry
        from indexer.cli import _is_indexable
        from indexer.grouper import density_group
        from indexer.wiki import sanitize_group_label

        cfg = load_config(root)
        if not (root / ".indexer.toml").exists():
            save_config(root, cfg)

        manifest = load_manifest(root)

        manifest_fixed = False
        for rel_path, entry in manifest.files.items():
            if not entry.wiki_page.startswith(cfg.wiki_dir + "/"):
                continue
            raw_label = entry.wiki_page[len(cfg.wiki_dir) + 1:].removesuffix(".md")
            expected_name = sanitize_group_label(raw_label)
            expected_path = f"{cfg.wiki_dir}/{expected_name}.md"
            if entry.wiki_page != expected_path:
                entry.wiki_page = expected_path
                manifest_fixed = True
        if manifest_fixed:
            save_manifest(root, manifest)

        tasks.update(task_id, status="running", progress=35, step="detecting_files")
        all_files = [f for f in all_tracked_files(root) if _is_indexable(f, cfg)]

        if manifest.last_indexed_commit is None:
            candidates = list(all_files)
        else:
            git_changed = changed_files_since(root, manifest.last_indexed_commit) if is_git_repo(root) else []
            stale = manifest.stale_files(root, all_files)
            candidates = list(set(git_changed + stale))

        missing_wiki = []
        for rel_path, entry in manifest.files.items():
            if not entry.component_ids:
                continue
            if entry.wiki_page.startswith(cfg.wiki_dir + "/"):
                raw_label = entry.wiki_page[len(cfg.wiki_dir) + 1:].removesuffix(".md")
                safe_name = sanitize_group_label(raw_label)
                actual_path = f"{cfg.wiki_dir}/{safe_name}.md"
            else:
                actual_path = entry.wiki_page
            wiki_path = root / actual_path
            if not wiki_path.exists() and rel_path not in candidates:
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
            tasks.update(task_id, status="done", progress=100, step="complete", detail="Nothing to sync")
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
                write_index_and_skill(root, cfg, index_entries, {}, "", [], 0, 0)
            webhook_url = _get_webhook_url(name)
            registry.register(name, root, url=repo_url, branches=repo_branches)
            tasks.update(task_id, status="done", progress=100, step="complete", result={
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
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())

        tasks.update(task_id, status="done", progress=100, step="complete", result={
            "name": name, "path": str(root),
            "has_vector_db": (root / info["config"].vector_store.persist_dir).exists(),
            "symbol_count": symbol_count, "synced": True,
            "webhook_url": webhook_url,
        })

    except subprocess.TimeoutExpired:
        tasks.update(task_id, status="failed", progress=10, step="git_pull", error="git pull timed out")
    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=str(e))
    finally:
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

    git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    git_cfg = ["-c", "http.followRedirects=true"]

    try:
        if clone_dir.exists() and (clone_dir / ".git").exists():
            tasks.update(task_id, status="running", progress=10, step="git_pull")
            subprocess.run(
                ["git"] + git_cfg + ["fetch", "--all"],
                cwd=clone_dir, capture_output=True, text=True, timeout=60, env=git_env,
            )
            if branch:
                subprocess.run(
                    ["git"] + git_cfg + ["checkout", branch],
                    cwd=clone_dir, capture_output=True, text=True, timeout=30, env=git_env,
                )
            subprocess.run(
                ["git"] + git_cfg + ["pull", "--rebase"],
                cwd=clone_dir, capture_output=True, text=True, timeout=60, env=git_env,
            )
        else:
            tasks.update(task_id, status="running", progress=10, step="git_clone")
            if clone_dir.exists():
                import shutil
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
                return

        _store_credentials(clone_dir, url, username, password, token)

        from indexer.config import Config, load_config, save_config
        from indexer.manifest import load_manifest, Manifest
        from indexer.git import all_tracked_files, current_commit, is_git_repo, changed_files_since
        from indexer.cli import _is_indexable, _ensure_cache_gitignore
        from indexer.hooks import install_hook

        root = clone_dir

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

        for idx, current_branch in enumerate(branches_to_index):
            if not current_branch:
                continue

            tasks.update(task_id, status="running", progress=40 + (50 * idx // len(branches_to_index)),
                         step=f"checkout_{current_branch}")

            # Checkout the branch
            subprocess.run(
                ["git"] + git_cfg + ["checkout", current_branch],
                cwd=root, capture_output=True, text=True, timeout=30, env=git_env,
            )
            subprocess.run(
                ["git"] + git_cfg + ["pull", "--rebase", "origin", current_branch],
                cwd=root, capture_output=True, text=True, timeout=60, env=git_env,
            )

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

            _run_indexing_pipeline(task_id, name, root, skip_deep, candidates, cfg, manifest, branch=current_branch)

        webhook_url = _get_webhook_url(name)
        info = registry.get(name)
        has_vectors = (clone_dir / info["config"].vector_store.persist_dir).exists()
        manifest_data = load_manifest(root)
        symbol_count = sum(len(entry.component_ids) for entry in manifest_data.files.values())

        tasks.update(task_id, status="done", progress=100, step="complete", result={
            "name": name,
            "path": str(clone_dir),
            "url": url,
            "has_vector_db": has_vectors,
            "symbol_count": symbol_count,
            "indexed": True,
            "webhook_url": webhook_url,
        })

    except subprocess.TimeoutExpired as e:
        cmd = e.cmd[0] if hasattr(e, 'cmd') else "git"
        tasks.update(task_id, status="failed", progress=0, step=cmd, error=f"timeout: {cmd} took too long")
    except Exception as e:
        tasks.update(task_id, status="failed", progress=0, step="unknown", error=str(e))


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
    top_k = body.get("top_k", 10)
    expand_depth = body.get("expand_depth", 1)
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
            else:
                where_clause = None
            for qv in all_query_vectors:
                hits = search(qv, cfg.vector_store, root, top_k=top_k * 2, where=where_clause)
                for h in hits:
                    h["repo"] = name
                    if h["id"] not in seen_ids:
                        seen_ids.add(h["id"])
                        all_hits.append(h)

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
            for h in expanded_hits:
                if h["id"] not in expanded_ids:
                    expanded_ids.add(h["id"])
                    expanded.append(h)
        all_hits = expanded

    return JSONResponse({
        "results": all_hits,
        "total": len(all_hits),
        "rewritten_queries": queries if len(queries) > 1 else None,
    })


async def trace_call(request: Request) -> JSONResponse:
    body = await _parse_body(request)
    symbol_id = body.get("symbol_id", "")
    direction = body.get("direction", "down")
    max_depth = body.get("max_depth", 3)
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
    line_start = body.get("line_start", 1)
    line_end = body.get("line_end", 1)
    repo = body.get("repo")
    padding = body.get("padding", 5)

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
    result = []
    for name in registry.list_names():
        info = registry.get(name)
        root = info["root"]
        has_vectors = (root / info["config"].vector_store.persist_dir).exists()
        manifest_path = root / ".indexer" / "manifest.json"
        symbol_count = 0
        last_synced_at = ""
        last_indexed_commit = ""
        if manifest_path.exists():
            from indexer.manifest import load_manifest
            manifest = load_manifest(root)
            symbol_count = sum(len(entry.component_ids) for entry in manifest.files.values())
            last_synced_at = manifest.indexed_at or ""
            if manifest.last_indexed_commit:
                last_indexed_commit = manifest.last_indexed_commit[:7]
        if not last_synced_at:
            try:
                from indexer.git import current_commit
                commit = current_commit(root)
                if commit:
                    import subprocess
                    out = subprocess.run(
                        ["git", "log", "-1", "--format=%cI", commit],
                        cwd=root, capture_output=True, text=True, timeout=10,
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
            "webhook_url": webhook_url,
            "has_vector_db": has_vectors,
            "symbol_count": symbol_count,
            "last_synced_at": last_synced_at,
            "last_indexed_commit": last_indexed_commit,
        })
    return JSONResponse({"repos": result})


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "repos": len(registry.repos)})


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
            content = md_file.read_text(encoding="utf-8", errors="replace")
            wiki_pages.append({
                "name": page_name,
                "path": str(md_file.relative_to(root)),
                "content": content,
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
    return JSONResponse({
        "name": repo_name,
        "path": str(root),
        "url": info.get("url", ""),
        "branches": info.get("branches", []),
        "webhook_url": webhook_url,
        "wiki_pages": wiki_pages,
        "manifest": manifest_data,
        "skill": skill_content,
        "has_vector_db": (root / cfg.vector_store.persist_dir).exists(),
        "last_synced_at": manifest_data.get("indexed_at", "") if manifest_data else "",
    })


async def multi_repo_skill(request: Request) -> JSONResponse:
    from indexer.wiki import sanitize_group_label
    from indexer.config import load_config
    from indexer.manifest import load_manifest

    all_repos = []
    for name, info in registry.repos.items():
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
    import hashlib, hmac
    return hmac.new(secret.encode(), name.encode(), hashlib.sha256).hexdigest()


def _verify_webhook_sign(name: str, sign: str) -> bool:
    expected = _webhook_sign(name)
    if not expected:
        return True
    import hmac
    return hmac.compare_digest(expected, sign)


_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


async def webhook_by_name(request: Request) -> JSONResponse:
    name = request.path_params.get("name", "")
    if not name or not registry.get(name):
        return JSONResponse({"error": f"repo '{name}' not registered"}, status_code=404)

    body = await request.body()

    if _WEBHOOK_SECRET:
        sign = request.query_params.get("sign", "")
        if not sign or not _verify_webhook_sign(name, sign):
            return JSONResponse({"error": "invalid sign"}, status_code=401)

    info = registry.get(name)
    repo_branches = info.get("branches", [])

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {}

    ref = payload.get("ref", "")
    webhook_branch = ""
    if ref.startswith("refs/heads/"):
        webhook_branch = ref[len("refs/heads/"):]

    target_branch = webhook_branch if (not repo_branches or webhook_branch in repo_branches) else ""
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
    if api_key:
        class _AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                path = request.url.path
                if path in ("/health", "/", "/static") or path.startswith(("/webhook/", "/static/")):
                    return await call_next(request)
                token = request.headers.get("Authorization", "").removeprefix("Bearer ")
                if token != api_key:
                    return JSONResponse({"error": "unauthorized"}, status_code=401)
                return await call_next(request)
        middleware.append(Middleware(_AuthMiddleware))

    app = Starlette(
        middleware=middleware,
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
    api_key = os.environ.get("REPO_WIKI_API_KEY", "")
    if api_key:
        script = f'<script>window._apiKey={json.dumps(api_key)};</script>'
        html = html.replace("</head>", script + "</head>")
    return HTMLResponse(html)


def _inject_credentials(
    url: str,
    username: str,
    password: str,
    token: str,
) -> str:
    parsed = urllib.parse.urlparse(url)
    if token:
        netloc = f"x-access-token:{urllib.parse.quote(token, safe='')}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urllib.parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    if username and password:
        netloc = f"{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urllib.parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    return url


def _sanitize_error(error_msg: str, url: str, username: str, password: str, token: str) -> str:
    safe = error_msg
    safe = safe.replace(url, "<REDACTED_URL>")
    if username:
        safe = safe.replace(username, "<REDACTED_USER>")
    if password:
        safe = safe.replace(password, "<REDACTED_PASS>")
    if token:
        safe = safe.replace(token, "<REDACTED_TOKEN>")
    return safe


def _store_credentials(
    clone_dir: Path,
    url: str,
    username: str,
    password: str,
    token: str,
) -> None:
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme
    host = parsed.hostname
    if parsed.port:
        host = f"{host}:{parsed.port}"

    subprocess.run(
        ["git", "remote", "set-url", "origin", url],
        cwd=clone_dir,
        capture_output=True,
        text=True,
    )

    if not (username or password or token):
        return

    credential_file = clone_dir / ".git" / "credentials"
    cred_store_path = str(credential_file)

    subprocess.run(
        ["git", "config", "credential.helper", f"store --file='{cred_store_path}'"],
        cwd=clone_dir,
        capture_output=True,
        text=True,
    )

    if token:
        cred_line = f"{scheme}://x-access-token:{urllib.parse.quote(token, safe='')}@{host}"
    elif username and password:
        cred_line = f"{scheme}://{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@{host}"
    else:
        return

    existing = ""
    if credential_file.exists():
        existing = credential_file.read_text()
    if cred_line not in existing:
        credential_file.write_text(existing.rstrip("\n") + "\n" + cred_line + "\n")
        os.chmod(credential_file, 0o600)

    gitignore = clone_dir / ".gitignore"
    cred_gitignore_entry = ".git/credentials"
    if gitignore.exists():
        content = gitignore.read_text()
        if cred_gitignore_entry not in content:
            gitignore.write_text(content.rstrip() + "\n" + cred_gitignore_entry + "\n")
    else:
        gitignore.write_text(cred_gitignore_entry + "\n")


def _resolve_repos(repo: str | None) -> list[tuple[str, dict]]:
    if repo:
        info = registry.get(repo)
        if not info:
            return []
        return [(repo, info)]
    return list(registry.repos.items())


def _trace_call_impl(
    symbol_id: str,
    cfg: Config,
    repo_root: Path,
    direction: str,
    max_depth: int,
) -> list[dict]:
    seed = get_by_ids([symbol_id], cfg.vector_store, repo_root)
    if not seed:
        return []

    result_nodes = [seed[0]]
    visited = {symbol_id}

    current_ids = set()
    meta = seed[0].get("metadata", {})
    if direction == "down":
        current_ids = set(_parse_json_list(meta.get("calls", "")))
    elif direction == "up":
        current_ids = set(_parse_json_list(meta.get("called_by", "")))

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

            nmeta = node.get("metadata", {})
            if direction == "down":
                next_ids.update(_parse_json_list(nmeta.get("calls", "")))
            elif direction == "up":
                next_ids.update(_parse_json_list(nmeta.get("called_by", "")))

        current_ids = next_ids - visited

    return result_nodes


def _expand_with_call_graph(
    hits: list[dict],
    cfg: Config,
    repo_root: Path,
    repo_name: str,
    depth: int = 1,
) -> list[dict]:
    expanded = list(hits)
    visited = {h["id"] for h in hits}

    for hit in hits:
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
                    node["repo"] = repo_name
                    expanded.append(node)

    return expanded


def _parse_json_list(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


async def _parse_body(request: Request) -> dict:
    try:
        body = await request.json()
    except Exception:
        return {}
    if not isinstance(body, dict):
        return {}
    return body
