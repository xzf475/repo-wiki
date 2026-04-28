# Codebase Index

## System Overview

The system is an MCP (Model Context Protocol) server implemented in `indexer/mcp_server.py`. It exposes several tools for code indexing and retrieval: `search_symbols_tool`, `trace_call_tool`, `get_source_context_tool`, and `list_repos`. Requests are guarded by a custom auth middleware (`_MCPAuthMiddleware`) that validates host permissions via `_allow_any_host`. The server likely delegates queries to an underlying indexer or database to fulfill symbol searches, call traces, and source context retrieval.
## Key Flows
- Incoming tool request → _MCPAuthMiddleware.dispatch → _allow_any_host → search_symbols_tool / trace_call_tool / get_source_context_tool → indexer query
- list_repos → repository enumeration from indexer
- _patched_method (likely a monkey-patched decorator) → any tool handler → modify behavior before dispatch

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/mcp_server.py | _patched_method, search_symbols_tool, trace_call_tool, get_source_context_tool, list_repos, search_symbols_tool, trace_call_tool, get_source_context_tool, _allow_any_host, _MCPAuthMiddleware, _MCPAuthMiddleware.dispatch |
## Last Indexed
Commit: 8ff9a71aaf42a2fbaa4f2caaebbf9626aa384dbd — 2026-04-28