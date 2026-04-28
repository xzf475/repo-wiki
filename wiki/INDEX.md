# Codebase Index

## System Overview

This system is a REST API server (likely built on FastAPI) that manages indexing tasks for code repositories. The core components are `TaskStore`, which handles the lifecycle of background tasks (create, get, cleanup); `RepoRegistry`, which persists repository configurations (register, unregister, get, list); and `_AuthMiddleware`, which provides token-based authentication for endpoints. The API exposes endpoints for registering/unregistering repos, triggering sync/rebuild tasks (single or all branches), querying task status, and handling webhook events, all orchestrated through task creation and registry lookups.
## Key Flows
- register_repo → _run_register_task → RepoRegistry.register → TaskStore.create → task execution
- sync_repo → TaskStore.create → sync handler → RepoRegistry.get → _run_all
- task_status → TaskStore.get → return status
- webhook_by_name → validate (auth?) → RepoRegistry.get → trigger sync/rebuild task
- _AuthMiddleware.dispatch → token validation → route handler (e.g., register_repo, list_repos)

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/rest_api.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: b7afe16298b8468527cd1be788e330f183a8e900 — 2026-04-28