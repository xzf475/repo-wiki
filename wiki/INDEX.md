# Codebase Index

## System Overview

This indexer service manages code repository indexing and retrieval via a REST API. The core components are `TaskStore` for tracking background indexing tasks and `RepoRegistry` for persisting repository metadata, both used by endpoints in `indexer/rest_api.py`. The `indexer/retrieval.py` module (not detailed here) handles retrieval logic. The service supports registering, syncing, rebuilding, and unregistering repos, with middleware for logging (`_LoggingMiddleware`) and authentication (`_AuthMiddleware`).
## Key Flows
- Register repo endpoint → `register_repo` → `_run_register_task` → `TaskStore.create` → background indexing
- Sync repo endpoint → `sync_repo` → `TaskStore.update` as task starts → triggers indexing of branches
- Health check → `health` endpoint → returns basic service status (no TaskStore dependency)
- Unregister repo → `unregister_repo` → `RepoRegistry.unregister` → `RepoRegistry._save` to persist change
- List repos → `list_repos` → `RepoRegistry.list_names` → returns all registered repo names

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/indexer.md | indexer/rest_api.py, indexer/retrieval.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: d388569df8ed5dd4a42a9685aac3e590b8c9cbc8 — 2026-04-29