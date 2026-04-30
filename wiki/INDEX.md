# Codebase Index

## System Overview

The system is a REST API built with a lightweight framework (likely FastAPI) that manages the lifecycle of repository indexing tasks. Its core components are the `TaskStore` class, which handles creation, retrieval, and cleanup of tasks via an in-memory or persistent store, and the `RepoRegistry` class, which manages repository metadata (register, unregister, update, list). Route handlers such as `register_repo`, `unregister_repo`, `sync_repo`, and `rebuild_repo` orchestrate these components, often pushing work to background tasks. Middleware classes `_AuthMiddleware` and `_LoggingMiddleware` add authentication and request logging across all endpoints. The entire API is defined in `indexer/rest_api.py`.
## Key Flows
- HTTP request → _AuthMiddleware (token validation) → route handler (e.g., register_repo) → TaskStore.create → response with task_id
- register_repo → validate_repo (repo URL/credentials) → RepoRegistry.register → _run_register_task (background) → TaskStore.update status
- sync_repo → RepoRegistry.get (repo config) → TaskStore.create → background worker runs sync_all_branches → RepoRegistry.update_meta
- webhook_by_name → RepoRegistry.get (by name) → validate_repo → sync_repo / reindex_repo → TaskStore.create → return task object
- unregister_repo → RepoRegistry.unregister → TaskStore._cleanup (remove related tasks) → response confirmation

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _rebuild_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 5faef9c2ce572f72c8d5432d03b7ebc275ad74d4 — 2026-04-30