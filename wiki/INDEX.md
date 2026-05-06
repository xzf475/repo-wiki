# Codebase Index

## System Overview

The system is a REST API for managing and indexing code repositories, implemented in `indexer/rest_api.py`. It uses `RepoRegistry` to persist repository metadata and `TaskStore` to manage indexing tasks via an asynchronous task queue. Endpoints like `register_repo`, `sync_repo`, and `reindex_repo` trigger task creation and orchestrate repository validation, syncing, and rebuilding. Middleware classes `_LoggingMiddleware` and `_AuthMiddleware` provide request logging and JWT-based authentication for all API routes.
## Key Flows
- POST /repos → register_repo → RepoRegistry.register → _run_register_task → TaskStore.create
- POST /sync/{name} → sync_repo → RepoRegistry.get → _run_all → TaskStore.create (sync task)
- POST /reindex/{name} → reindex_repo → RepoRegistry.get → _run_all → TaskStore.create (reindex task)
- POST /webhook/{name} → webhook_by_name → _index_page → TaskStore.create (partial index)
- GET /health → health → RepoRegistry.list_names (liveness check)

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.items, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _invalid_body_handler, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: fe25e87763f5633d106ed3ba92ea377c16cab478 — 2026-05-06