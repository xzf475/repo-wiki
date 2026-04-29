# Codebase Index

## System Overview

The system is a REST API (likely FastAPI) defined in `indexer/rest_api.py` for managing code repository indexing and synchronization. It exposes endpoints to register, unregister, sync, rebuild, and reindex repositories, with task management via `TaskStore` and persistent repo metadata via `RepoRegistry`. Request processing is layered with `_LoggingMiddleware` and `_AuthMiddleware` for audit and JWT authentication, and all heavy operations are dispatched as asynchronous tasks. The overall architecture centers on stateless route handlers that delegate to store and registry components, with status polling endpoints to track progress.
## Key Flows
- _AuthMiddleware.dispatch (JWT validation) → route handler (e.g., register_repo, list_repos, health)
- register_repo → _run_register_task → TaskStore.create (task) → RepoRegistry.register (persist metadata) → task_status (polling)
- sync_repo → TaskStore.create (sync task) → RepoRegistry.get (lookup repo) → _rebuild_all? → task_status
- webhook_by_name → RepoRegistry.get (lookup webhook) → trigger sync or rebuild → task_status
- health → simple response; also used by monitoring to verify auth/logging middleware is active

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _rebuild_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 3f01d0666d9aa552f77ee217406d68705b18d0ee — 2026-04-29