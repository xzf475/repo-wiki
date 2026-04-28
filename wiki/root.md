# ./

## Overview

This module implements an MCP (Model Context Protocol) server that exposes the code indexer’s capabilities—symbol search, call graph tracing, and source context retrieval—as AI-accessible tools. It solves the problem of making a rich static analysis backend consumable by LLM agents or chat interfaces via a standardized tool protocol. Two server factories exist: `create_server` wires tools directly to in-process indexer functions (e.g., `search_symbols`, `trace_call`), while `create_api_server` delegates all requests to a remote indexing service via HTTP. Authentication is enforced by `_MCPAuthMiddleware`, an ASGI middleware that validates Auth0 JWTs and wraps each tool handler through `_apply_mcp_auth`. The module thus bridges the indexer’s internal data structures to external MCP clients, with a pluggable auth layer and a remote-proxy mode for distributed deployments.

## Modules
| File | Purpose |
|------|---------|
| indexer/mcp_server.py | MCP server providing semantic code search, call graph tracing, and source context tools |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Wraps MCP handler with Auth0 JWT authentication, returns JSON error on failure |
| `indexer/mcp_server.py::create_server` | function | Creates a FastMCP server with search, trace, and source context tools |
| `indexer/mcp_server.py::create_api_server` | function | Creates a FastMCP API server delegating to a remote indexing service |
| `indexer/mcp_server.py::_patched_method` | function | Patches a method to apply MCP authentication middleware |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols across repos via API with optional query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph via API across specified repo with depth control |
| `indexer/mcp_server.py::get_source_context_tool` | function | Fetches source code context via API for given repo and line range |
| `indexer/mcp_server.py::_api_get` | function | Performs a GET request to the indexer API and returns parsed JSON |
| `indexer/mcp_server.py::_api_post` | function | Performs a POST request to the indexer API with JSON body |
| `indexer/mcp_server.py::list_repos` | function | Lists all registered repositories with names and basic stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols across repos via API with optional query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph via API across specified repo with depth control |
| `indexer/mcp_server.py::get_source_context_tool` | function | Fetches source code context via API for given repo and line range |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware that validates JWT tokens for MCP endpoints |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Dispatches request after extracting and validating Bearer token |
## Data Flows
- Client opens MCP connection → FastMCP routes tool call → `_apply_mcp_auth` wraps handler → `_MCPAuthMiddleware.dispatch` validates Bearer token → tool function runs (e.g., `search_symbols_tool` → `_api_post` → remote indexer API) → JSON response returned to client.
- Local mode: Client requests symbol search → `search_symbols_tool` invoked → calls in-process `search_symbols` with `repo`, `symbol`, `rewrite` params → returns joined results list as string.
- Remote mode: Client requests trace call graph → `trace_call_tool` calls `_api_post` → POST to `/api/trace_call` with JSON body → response decoded via `loads` → returns formatted trace string.
- Authentication failure flow: HTTP request to `/mcp/...` → `_MCPAuthMiddleware.dispatch` extracts token → JWT validation fails → returns `JSONResponse` with status 401 and error details, never reaching the tool handler.
## Design Constraints
- The `_apply_mcp_auth` function monkey‑patches the original handler method by replacing it with `_patched_method`, which inserts `_MCPAuthMiddleware` as a wrapper. This means auth is injected at the method level, not the router level.
- The middleware strips the leading `/mcp/` prefix from `scope['path']` before passing to the underlying application, so downstream handlers must not expect that prefix.
- All API calls in remote mode (`_api_get`, `_api_post`) use blocking `urllib` calls inside tool handlers. This is safe only because FastMCP runs tool handlers in a thread pool; a truly async implementation would require aiohttp.
- Authentication is optional: if environment variables `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET` are missing, `_apply_mcp_auth` returns the original handler unmodified, disabling JWT checks entirely.
- Local mode tools (`create_server`) require the indexer’s in‑memory data to be pre‑loaded (e.g., via `indexer/__init__.py` initialization). The remote mode tools (`create_api_server`) have no such requirement and rely on the external API being available.
- The tool functions (e.g., `search_symbols_tool`, `trace_call_tool`) accept optional parameters like `api_key` for remote authentication and `rewrite` for query rewriting; these parameters are passed through to the underlying API call, but the MCP tool schema does not enforce their presence.
## Relationships
- **Calls:** FastMCP, JSONResponse, Request, _MCPAuthMiddleware, _api_get, _api_post, _apply_mcp_auth, _orig_method, append, call_next, cwd, dumps, encode, get, get_source_context, join, len, load_config, loads, read, removeprefix, rstrip, search_symbols, tool, trace_call, urlopen
- **Called by:** indexer/cli.py::serve, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool
- **Imports from:** __future__.annotations, indexer.config.load_config, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, json, mcp.server.fastmcp.FastMCP, pathlib.Path, starlette.middleware.base.BaseHTTPMiddleware, starlette.responses.JSONResponse, urllib.error, urllib.request
## Entry Points
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
