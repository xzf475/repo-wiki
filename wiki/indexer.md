# indexer/

## Overview

The indexer module provides a code indexing and retrieval layer that exposes semantic search, call-graph tracing, and source context extraction to AI agents via the Model Context Protocol (MCP). It solves the problem of enabling LLMs to navigate large codebases by abstracting over local filesystem access or a REST API backend. Two server creation functions (create_server for direct mode, create_api_server for remote mode) build FastMCP instances with tools like search_symbols_tool, trace_call_tool, and get_source_context_tool. Key supporting classes include RepoRegistry (manages registered repositories with JSON persistence in a temp directory) and TaskStore (tracks async task statuses with hourly cleanup). An authentication middleware (_MCPAuthMiddleware) can be monkey-patched onto the direct server to enforce Bearer token validation. This module acts as a bridge between code indexing infrastructure and LLM tool-use interfaces.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository registration and indexing tasks |
| indexer/mcp_server.py | MCP server for code symbol search and call graph tracing |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Patches MCP server method to validate Bearer token from Authorization header |
| `indexer/mcp_server.py::create_server` | function | Builds FastMCP server with local search, trace, context tools and auth middleware |
| `indexer/mcp_server.py::create_api_server` | function | Builds FastMCP server using REST API backend for search, trace, context tools |
| `indexer/mcp_server.py::_patched_method` | function | Replaces original MCP method with auth-checking wrapper returning JSON 401 on invalid token |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches code symbols by semantic query across repos via REST API with expansion |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph up/down from a symbol via REST API up to max_depth hops |
| `indexer/mcp_server.py::get_source_context_tool` | function | Returns source code lines around a file range via REST API with padding |
| `indexer/mcp_server.py::_api_get` | function | Sends HTTP GET to REST API and parses JSON response |
| `indexer/mcp_server.py::_api_post` | function | Sends HTTP POST with JSON body to REST API and parses response |
| `indexer/mcp_server.py::list_repos` | function | Lists registered repositories with names, descriptions, tags, and basic stats via API |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches code symbols by semantic query across repos via REST API with expansion |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph up/down from a symbol via REST API up to max_depth hops |
| `indexer/mcp_server.py::get_source_context_tool` | function | Returns source code lines around a file range via REST API with padding |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware that validates Bearer token from Authorization header |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Checks token validity; returns 401 JSON error on failure, else calls next middleware |
| `indexer/rest_api.py::_get_repo_lock` | function | Returns an asyncio Lock dedicated to a specific repo name |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for async task statuses with auto-cleanup of old entries |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes empty dict for task storage |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks older than one hour from internal dict |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task entry with unique UUID and current timestamp |
| `indexer/rest_api.py::TaskStore.get` | method | Returns task data for given task id, or None |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task's status and result, sets last_updated to now |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch name via git ls-remote HEAD |
| `indexer/rest_api.py::_discover_remote_branches` | function | Lists remote branches matching glob pattern using git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repositories with persistence to disk as JSON |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Ensures temp directory exists for storing registry data |
| `indexer/rest_api.py::RepoRegistry._save` | method | Writes repository registry as JSON to temp file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from file, detects default branch for each repo |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repository after config validation and persists |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository from registry and persists |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository config for given name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns alphabetically sorted list of registered repo names |
| `indexer/rest_api.py::register_repo` | function | Validates and registers a new repository, returning async task ID |
| `indexer/rest_api.py::task_status` | function | Returns the status and result of a given async task ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repository index files, reports missing or stale data |
| `indexer/rest_api.py::sync_repo` | function | Queues a sync task for a given repository, returns task ID |
| `indexer/rest_api.py::rebuild_repo` | function | Queues a full rebuild task for a given repository |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all remote branches for a repository, returns task |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds indexes for all remote branches of a repository |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Orchestrates full indexing pipeline: parse, enrich, vectorize, and write results |
| `indexer/rest_api.py::_run_rebuild_task` | function | Rebuilds entire index for a repository from scratch |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs index incrementally by detecting changed files and re-indexing |
| `indexer/rest_api.py::_run_register_task` | function | Registers a repository, acquiring lock to prevent concurrent operations |
| `indexer/rest_api.py::_run_register_task_inner` | function | Performs repository registration: inject credentials, index, discover branches |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository, removes its index and manifest |
| `indexer/rest_api.py::search_symbols` | function | Searches indexed symbols, expands results with call graph, returns sorted JSON |
| `indexer/rest_api.py::trace_call` | function | Traces call chain (callers/callees) of a symbol using stored graph |
| `indexer/rest_api.py::get_source_context` | function | Retrieves source code lines around a given line number in a file |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repositories with current commit and webhook URL |
| `indexer/rest_api.py::health` | function | Returns health status with number of indexed repos |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed metadata and file list for a single repo |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates skill definitions across multiple repositories |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook URL with HMAC signature for notifications |
| `indexer/rest_api.py::_webhook_sign` | function | Signs webhook payload with HMAC-SHA256 using secret key |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies incoming webhook signature matches calculated HMAC |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook events by name, triggers re-indexing |
| `indexer/rest_api.py::create_app` | function | Creates and configures the Starlette ASGI application with middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the main index.html page with repo listings |
| `indexer/rest_api.py::_inject_credentials` | function | Injects username and token into repository URL for authentication |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error messages to hide sensitive repository URLs |
| `indexer/rest_api.py::_store_credentials` | function | Stores Git credentials in local cache with restrictive file permissions |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repository IDs from query parameters into a list |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements call trace by recursively fetching callees/callers by ID |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results with related symbols from call graph |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a list of items |
| `indexer/rest_api.py::_parse_body` | function | Parses FastAPI request body into Python dict or list |
| `indexer/rest_api.py::_run_all` | function | Runs all rebuild (full re-index) tasks for registered repos |
| `indexer/rest_api.py::_run_all` | function | Runs all rebuild (full re-index) tasks for registered repos |
| `indexer/rest_api.py::_LoggingMiddleware` | class | Middlewares that logs request duration and method |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs incoming request method, path, and duration after response |
| `indexer/rest_api.py::_AuthMiddleware` | class | Validates incoming requests using shared secret token |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks Authorization header against shared secret; returns 401 if invalid |
## Data Flows
- Client calls MCP search_symbols tool → local implementation (search_symbols) or REST API call (_api_post) → returns formatted list of matching symbols.
- Client calls MCP trace_call tool → local trace_call or REST API call (_api_post) → returns up/down call graph up to max_depth.
- Client calls MCP get_source_context tool → local get_source_context or REST API call (_api_post) → returns source lines around given file+range.
- REST API registration: POST /register → RepoRegistry.register → validates config with load_config → saves registry to temp JSON file.
## Design Constraints
- The MCP authentication patching (_apply_mcp_auth) is only applied when create_server is called directly; the REST API backend mode (create_api_server) has no auth layer.
- TaskStore entries older than 1 hour are silently removed on every create() call, so long-running tasks may expire before being polled.
- RepoRegistry persistence uses a single temp JSON file (no database); data is lost on machine reboot unless re-registered.
- Default branch detection (_detect_default_branch) requires network access to the remote git endpoint and may silently fail for unreachable repos.
- The context tool (get_source_context_tool) returns raw code lines without any sanitization; callers must handle potentially large output.
- The direct server mode (create_server) uses the current working directory (cwd) as the base path, making it sensitive to the process's startup directory.
## Relationships
- **Calls:** FastMCP, HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Request, Route, Starlette, StaticFiles, _MCPAuthMiddleware, _api_get, _api_post, _apply_mcp_auth, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _orig_method, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, cwd, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_running_loop, get_source_context, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, search_symbols, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, tool, trace_call, unlink, unregister, update, update_manifest, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
- **Imports from:** __future__.annotations, asyncio, collections.defaultdict, datetime.datetime, datetime.timezone, fnmatch, hashlib, hmac, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.utils.load_env_file, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.wiki.IndexEntry, indexer.wiki.build_index, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, json, logging, mcp.server.fastmcp.FastMCP, os, pathlib.Path, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.error, urllib.parse, urllib.request, uuid
## Entry Points
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `TaskStore`
- `RepoRegistry`
- `register_repo`
- `task_status`
- `validate_repo`
- `sync_repo`
- `rebuild_repo`
- `sync_all_branches`
- `rebuild_all_branches`
- `unregister_repo`
- `list_repos`
- `health`
- `repo_detail`
- `multi_repo_skill`
- `webhook_by_name`
