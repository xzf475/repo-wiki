# ./

## Overview

This module implements an MCP (Model Context Protocol) server that exposes code indexing capabilities as tools for LLM agents. It supports two deployment modes via `create_server` (direct, using a local indexer and configuration) and `create_api_server` (proxy, forwarding requests to an external API). Authentication is enforced by the `_MCPAuthMiddleware` class (validates Auth0 JWT tokens from the Authorization header), applied through monkey-patching of FastMCP's `add_middleware` method. Tools registered include `search_symbols_tool`, `trace_call_tool`, `get_source_context_tool`, and `list_repos`, each accepting optional repo scoping and output rewriting parameters.

## Modules
| File | Purpose |
|------|---------|
| indexer/mcp_server.py | MCP server exposing code search, trace, and context tools |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Wraps FastMCP with Auth0 JWT authentication middleware |
| `indexer/mcp_server.py::create_server` | function | Creates FastMCP server instance, loads config, registers tools, applies auth |
| `indexer/mcp_server.py::create_api_server` | function | Creates FastMCP server that proxies tools to external API with auth |
| `indexer/mcp_server.py::_patched_method` | function | Patches FastMCP's add_middleware to inject Auth0 JWT check |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols by semantic query with call graph expansion and optional repo/rewrite |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph from symbol up/down to max depth, optionally scoped to a repo |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code around a line range with padding, optionally per repo |
| `indexer/mcp_server.py::_api_get` | function | Performs HTTP GET to internal API, returns parsed JSON |
| `indexer/mcp_server.py::_api_post` | function | Performs HTTP POST to internal API with JSON payload, returns parsed JSON |
| `indexer/mcp_server.py::list_repos` | function | MCP tool: lists all registered repositories with names and stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols by semantic query with call graph expansion and optional repo/rewrite |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph from symbol up/down to max depth, optionally scoped to a repo |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code around a line range with padding, optionally per repo |
| `indexer/mcp_server.py::_allow_any_host` | function | Middleware that allows any host in MCP authentication |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware class validating Auth0 JWT tokens on each request |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Dispatches request after verifying JWT token from Authorization header |
## Data Flows
- Client connects → triggers tool call (e.g., search_symbols_tool) → handled directly via get()/search_symbols() (direct mode) or proxied via _api_post (proxy mode) → returns result
- Client sends request → _MCPAuthMiddleware.dispatch extracts Authorization header → validates JWT → passes to underlying app or returns 401 JSONResponse
- create_server loads config → registers tools → applies auth middleware via _apply_mcp_auth (patches add_middleware) → starts FastMCP server
- create_api_server creates FastMCP → registers proxy tools (calling _api_get/_api_post) → applies auth → starts server
## Design Constraints
- Auth middleware is applied by monkey-patching FastMCP.add_middleware (preserving the original method) to inject JWT validation before downstream middleware.
- The server operates in exactly one of two mutually exclusive modes: direct (create_server) or proxy (create_api_server); no hybrid mode exists.
- In proxy mode, all tool implementations delegate to internal HTTP helpers (_api_get, _api_post) that strip trailing whitespace (rstrip) from JSON responses.
- The `join` function (likely os.path.join or equivalent) is called pervasively for path normalization; its specific semantics (e.g., handling of absolute vs relative paths) are not defined at module level.
- The `get` function serves as a global configuration/dependency accessor; tools depend on it for shared state (e.g., indexer instance, config values) and must be called after setup.
- The `_allow_any_host` middleware bypasses host checks in MCP authentication, implying that under certain configurations the host header is not validated.
## Relationships
- **Calls:** FastMCP, JSONResponse, Request, _api_get, _api_post, _apply_mcp_auth, _inner, _orig_method, add_middleware, append, call_next, cwd, dumps, encode, get, get_source_context, join, len, load_config, loads, read, removeprefix, rstrip, search_symbols, tool, trace_call, urlopen
- **Called by:** indexer/cli.py::serve, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool
- **Imports from:** __future__.annotations, indexer.config.Config, indexer.config.load_config, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, json, mcp.server.fastmcp.FastMCP, pathlib.Path, starlette.middleware.base.BaseHTTPMiddleware, starlette.responses.JSONResponse, urllib.error, urllib.request
## Entry Points
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
