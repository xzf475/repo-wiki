# Codebase Index

## System Overview

The system is a FastAPI-based REST API service for indexing and managing code repositories, located in indexer/rest_api.py. It relies on two core components: TaskStore for asynchronous task orchestration (create, get, update, cleanup) and RepoRegistry for persisting repository metadata (name, branches, status). API endpoints (register_repo, sync_repo, reindex_repo, etc.) interact with these components, while _AuthMiddleware and _LoggingMiddleware provide cross-cutting authentication and request logging.
## Key Flows
- register_repo → RepoRegistry.register → _run_register_task → TaskStore.create → async indexing task
- sync_repo → RepoRegistry.get → TaskStore.create (sync task) → RepoRegistry.update_meta
- _AuthMiddleware.dispatch → JWT validation → route handler (e.g., repo_detail, update_repo_meta)
- webhook_by_name → RepoRegistry.get → webhook payload handling → TaskStore.create (reindex/rebuild)
- rebuild_all_branches → RepoRegistry.list_names → _rebuild_all → TaskStore.create per branch → RepoRegistry.update_meta

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _rebuild_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: 25af1b81f9b1164a383f4f21e87dad62cd175e08 — 2026-04-30