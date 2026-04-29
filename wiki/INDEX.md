# Codebase Index

## System Overview

The system is a REST API for indexing and managing code repositories, built with FastAPI (likely) and exposed via `indexer/rest_api.py`. Main components include `TaskStore` for persistent task management (create, get, update, cleanup), `RepoRegistry` for repo metadata (register, unregister, list, update meta), and a set of route handlers (`register_repo`, `unregister_repo`, `sync_repo`, `rebuild_repo`, `sync_all_branches`, `health`, `webhook_by_name`) with middleware layers for logging (`_LoggingMiddleware`) and authentication (`_AuthMiddleware`). The `multi_repo_skill` entry point suggests a batched operation across repos, and webhooks trigger index updates.
## Key Flows
- POST /register_repo → validate_repo → RepoRegistry.register → TaskStore.create (index task) → _run_register_task
- POST /unregister_repo → RepoRegistry.unregister → TaskStore.create (cleanup task) → _run_all
- POST /sync_all_branches → sync_all_branches → RepoRegistry.list_names → TaskStore.create (sync tasks per repo) → _run_all
- POST /webhook_by_name → webhook_by_name → RepoRegistry.get → validate → TaskStore.create (rebuild task) → _run_all
- GET /repos → list_repos → RepoRegistry.list_names → RepoRegistry.get (each) → return repo detail

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 02415dfb9ec17fdba069d385d052ce25d82caa8c — 2026-04-29