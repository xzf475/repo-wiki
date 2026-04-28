# Codebase Index

## System Overview

This system is a Model Context Protocol (MCP) server for code indexing, implemented primarily in `indexer/mcp_server.py`. It exposes tools for searching symbols (`search_symbols_tool`), tracing function calls (`trace_call_tool`), retrieving source code context (`get_source_context_tool`), and listing repositories (`list_repos`). All requests pass through `_MCPAuthMiddleware.dispatch` for JWT-based authentication before reaching the tool handlers. The server relies on an underlying code database (likely SQLite or vector store) to serve indexed metadata and source code.
## Key Flows
- HTTP request → _MCPAuthMiddleware.dispatch → token validation → route to tool handler
- search_symbols_tool → query index DB (symbol table) → return matching symbols with locations
- trace_call_tool → traverse call graph DB → return call chain (caller/callee pairs) with source references
- get_source_context_tool → fetch source code from DB → return surrounding context lines for a symbol
- list_repos → query repo metadata DB → return list of repositories with last indexed timestamp

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/mcp_server.py | _patched_method, search_symbols_tool, trace_call_tool, get_source_context_tool, list_repos, search_symbols_tool, trace_call_tool, get_source_context_tool, _MCPAuthMiddleware.dispatch |
## Last Indexed
Commit: 19dfa17df824ef39a5a521ee581e51d7e39db627 — 2026-04-28