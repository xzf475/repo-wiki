from __future__ import annotations
import copy
import json
import logging
import tempfile
import threading
from pathlib import Path

from indexer.config import load_config

logger = logging.getLogger("repo-wiki-api")

_repo_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()
_MAX_LOCKS = 1000


def _get_repo_lock(name: str) -> threading.Lock:
    with _locks_lock:
        if name not in _repo_locks:
            if len(_repo_locks) >= _MAX_LOCKS:
                stale = [k for k, v in _repo_locks.items() if not v.locked()]
                for k in stale[:len(_repo_locks) - _MAX_LOCKS + 1]:
                    del _repo_locks[k]
            _repo_locks[name] = threading.Lock()
        return _repo_locks[name]


class RepoRegistry:
    def __init__(self, repos_dir: Path | None = None):
        self.repos: dict[str, dict] = {}
        self.repos_dir = repos_dir or Path(tempfile.gettempdir()) / "repo_wiki_repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self.repos_dir / "repos_registry.json"
        self._lock = threading.RLock()

    def _save(self):
        data = {
            name: {
                "root": str(info["root"]),
                "url": info.get("url", ""),
                "branches": info.get("branches", []),
                "branch_rule": info.get("branch_rule", ""),
                "description": info.get("description", ""),
                "tags": info.get("tags", []),
            }
            for name, info in self.repos.items()
        }
        tmp = self._registry_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(self._registry_file)

    def _load(self):
        from indexer.git_ops import _detect_default_branch
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
                    description = ""
                    tags = []
                else:
                    path_str = entry.get("root", "")
                    url = entry.get("url", "")
                    branch_rule = entry.get("branch_rule", "")
                    description = entry.get("description", "")
                    tags = entry.get("tags", [])
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
                    self.repos[name] = {"root": repo_root, "config": cfg, "url": url, "branches": branches, "branch_rule": branch_rule, "description": description, "tags": tags}
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load repo registry: %s", e)

    def register(self, name: str, repo_root: Path, url: str = "", branches: list[str] | None = None, branch_rule: str = "", description: str | None = None, tags: list[str] | None = None):
        with self._lock:
            existing = self.repos.get(name, {})
            cfg = load_config(repo_root)
            self.repos[name] = {
                "root": repo_root,
                "config": cfg,
                "url": url,
                "branches": branches or [],
                "branch_rule": branch_rule,
                "description": description if description is not None else existing.get("description", ""),
                "tags": tags if tags is not None else existing.get("tags", []),
            }
            self._save()
        logger.info("Registered repo '%s' at %s", name, repo_root)

    def unregister(self, name: str):
        with self._lock:
            if name in self.repos:
                info = self.repos[name]
                del self.repos[name]
                self._save()
                if info:
                    try:
                        from indexer.vector_store import evict_client
                        repo_path = Path(info.get("root", "."))
                        cfg = info.get("config")
                        if cfg:
                            evict_client(str(repo_path / cfg.vector_store.persist_dir))
                    except Exception as e:
                        logger.debug("evict_client failed for %s: %s", name, e)
            logger.info("Unregistered repo '%s'", name)
        with _locks_lock:
            lock = _repo_locks.get(name)
            if lock and not lock.locked():
                _repo_locks.pop(name, None)

    def get(self, name: str) -> dict | None:
        with self._lock:
            entry = self.repos.get(name)
            return copy.deepcopy(entry) if entry else None

    def list_names(self) -> list[str]:
        with self._lock:
            return sorted(self.repos.keys())

    def items(self) -> list[tuple[str, dict]]:
        with self._lock:
            return list(self.repos.items())

    def update_meta(self, name: str, description: str | None = None, tags: list[str] | None = None, branch_rule: str | None = None):
        with self._lock:
            if name not in self.repos:
                raise ValueError(f"repo '{name}' not found")
            info = self.repos[name]
            if description is not None:
                info["description"] = description
            if tags is not None:
                info["tags"] = tags
            if branch_rule is not None:
                info["branch_rule"] = branch_rule
            self._save()
        logger.info("Updated meta for repo '%s'", name)
