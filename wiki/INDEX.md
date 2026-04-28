# Codebase Index

## System Overview

The system is a REST API for managing indexing tasks across multiple code repositories, implemented primarily in `indexer/rest_api.py`. Main components are `TaskStore` (manages async task lifecycle and cleanup), `RepoRegistry` (persists repository metadata to disk), and `_AuthMiddleware` (JWT-based authentication). The API exposes endpoints for registering, syncing, rebuilding, and unregistering repos, as well as health checks and webhook handling; all flows coordinate between the middleware, the task store, and the registry.
## Key Flows
- Auth Middleware → _AuthMiddleware.dispatch → route handler (e.g., register_repo, sync_repo)
- Register repository → register_repo → RepoRegistry.register → _run_register_task → TaskStore.create → auto-triggers sync_all_branches
- Sync/rebuild repository → sync_repo/rebuild_repo → TaskStore.create → repo_detail (status polling) or webhook_by_name → _run_all
- Webhook trigger → webhook_by_name → validate_repo → _run_register_task or sync_all_branches → TaskStore tasks
- Health check → health → TaskStore._cleanup → returns status (active/recent tasks count, registry summary)

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 72695493cfab23ad693127817e79f16a5325ea40 — 2026-04-28