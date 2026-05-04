# Codebase Index

## System Overview

The codebase implements a REST API service for managing and indexing Git repositories, defined entirely within `indexer/rest_api.py`. Core components are `TaskStore` (async task queue), `RepoRegistry` (persistent repository metadata), and two middleware classes (`_LoggingMiddleware`, `_AuthMiddleware`) for request logging and Auth0 JWT authentication. API endpoints such as `register_repo`, `sync_repo`, `reindex_repo`, and `webhook_by_name` orchestrate operations by delegating to `TaskStore` for background execution and `RepoRegistry` for state management.
## Key Flows
- POST /register -> register_repo -> RepoRegistry.register -> _run_register_task (background) -> validate_repo -> sync_repo
- POST /sync?repo_name -> sync_repo -> RepoRegistry.get -> TaskStore.create -> sync_repo (background task)
- POST /rebuild_all -> rebuild_all_branches -> TaskStore.create -> _rebuild_all (background) -> reindex each repo
- POST /webhook?name -> webhook_by_name -> rep.trigger (reindex / sync) -> TaskStore.create -> corresponding background task
- Any request -> _AuthMiddleware.dispatch (JWT validation) -> route handler -> optional _LoggingMiddleware.dispatch

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, RepoRegistry.update_meta, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, reindex_repo, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, update_repo_meta, multi_repo_skill, webhook_by_name, _index_page, _run_all, _rebuild_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: ab8fae122b61e58816c91a41c76d05114a5599fc — 2026-05-04