# Codebase Index

## System Overview

The system is a REST API service for managing code repository indexing, built with aiohttp. The main module is `indexer/rest_api.py`, which provides endpoints for repository registration, synchronization, reindexing, and task tracking. Core components include `RepoRegistry` for persisting repo metadata (likely stored as JSON), `TaskStore` for tracking async operations (cleanup, create, get, update), and middleware for authentication (`_AuthMiddleware`) and logging (`_LoggingMiddleware`). These components interact via route handlers (e.g., `register_repo`, `sync_repo`) that orchestrate calls to Registry, TaskStore, and indexing logic.
## Key Flows
- HTTP request → _AuthMiddleware → route handler → RepoRegistry.register → _run_register_task → TaskStore.create → _cleanup
- HTTP request → _AuthMiddleware → route handler → sync_repo → RepoRegistry.get → sync_all_branches → rebuild_all_branches → _rebuild_all → _index_page → TaskStore.update
- HTTP request → _AuthMiddleware → route handler → unregister_repo → RepoRegistry.unregister → RepoRegistry._save → TaskStore._cleanup
- HTTP request → _AuthMiddleware → route handler → list_repos → RepoRegistry.list_names → return JSON response
- HTTP request → _AuthMiddleware → route handler → health → return status (includes TaskStore, RepoRegistry state checks)

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _rebuild_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 0a35b869744e450bafc9ac2cfe291424e8cb6049 — 2026-04-30