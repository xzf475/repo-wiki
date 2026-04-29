# Codebase Index

## System Overview

The system is a code indexing service with dual interfaces: an MCP (Model Context Protocol) server exposing tools for symbol search, call tracing, and source context retrieval, and a REST API for repository management (register, sync, rebuild, unregister) and task tracking. Core components include the `indexer/mcp_server.py` serving MCP tools, `indexer/rest_api.py` hosting REST endpoints, `TaskStore` for asynchronous task creation and lifecycle, and `RepoRegistry` for persistent repository state. Middleware layers (`_MCPAuthMiddleware`, `_LoggingMiddleware`, `_AuthMiddleware`) provide authentication and logging across both interfaces, while a webhook endpoint (`webhook_by_name`) enables event-driven reindexing.
## Key Flows
- MCP client → _MCPAuthMiddleware.dispatch → search_symbols_tool (symbol lookup)
- REST client → _AuthMiddleware.dispatch → register_repo → TaskStore.create → _run_register_task → RepoRegistry.register
- REST client → sync_repo → TaskStore.create → (sync task targeting a repository)
- Webhook POST → webhook_by_name → validates event → triggers indexing tasks via TaskStore.create
- Any request → _LoggingMiddleware.dispatch → _AuthMiddleware.dispatch → route handler (REST or MCP)

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/indexer.md | indexer/mcp_server.py, indexer/rest_api.py | _patched_method, search_symbols_tool, trace_call_tool, get_source_context_tool, list_repos, search_symbols_tool, trace_call_tool, get_source_context_tool, _MCPAuthMiddleware.dispatch, TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update, RepoRegistry, RepoRegistry.__init__, RepoRegistry._save, RepoRegistry._load, RepoRegistry.register, RepoRegistry.unregister, RepoRegistry.get, RepoRegistry.list_names, register_repo, task_status, validate_repo, sync_repo, rebuild_repo, sync_all_branches, rebuild_all_branches, _run_register_task, unregister_repo, list_repos, health, repo_detail, multi_repo_skill, webhook_by_name, _index_page, _run_all, _run_all, _LoggingMiddleware, _LoggingMiddleware.dispatch, _AuthMiddleware, _AuthMiddleware.dispatch |
## Last Indexed
Commit: e7850e36764e1724c1c97b7a4d497e9bded3e0a3 — 2026-04-29