# Codebase Index

## System Overview

The indexer service manages repository registration and indexing tasks via a REST API (indexer/rest_api.py). Core components are the RepoRegistry (persistent repo metadata store) and TaskStore (asynchronous task queue for indexing operations). The service exposes endpoints for registering/unregistering repos, triggering sync/rebuild, and checking status, with authentication and logging middleware wrapping all requests.
## Key Flows
- register_repo endpoint → validate_repo → RepoRegistry.register → _run_register_task → TaskStore.create → async indexer task
- sync_repo endpoint → RepoRegistry.get → TaskStore.create (sync task) → _index_page → repo retrieval logic
- webhook_by_name endpoint → RepoRegistry.get → TaskStore.create (rebuild task) → rebuild_repo → _run_all
- health endpoint → TaskStore.get (status check) → return health status
- request → _AuthMiddleware.dispatch (JWT validation) → route handler → response → _LoggingMiddleware.dispatch

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/indexer.md | indexer/rest_api.py, indexer/retrieval.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: d3851c5d44cae9ec77ac8ec7a02d776059b3e901 — 2026-04-29