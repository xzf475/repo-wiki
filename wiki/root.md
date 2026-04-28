# ./

## Overview

This module exposes a REST API for managing Git repository indexing tasks. It solves the problem of triggering, tracking, and coordinating long-running indexing operations (clone, sync, rebuild) across multiple repositories without blocking HTTP handlers. The `RepoRegistry` class persists registered repo metadata (URL, branches, credentials) to a JSON file in a temp directory, while `TaskStore` provides an in-memory task state store with automatic expiration of stale entries. Key functions like `register_repo`, `sync_repo`, `rebuild_repo` and their `_run_*` counterparts encapsulate async execution via `asyncio.get_running_loop().run_in_executor()`, ensuring each repo operation is serialized by a threading lock (`_get_repo_lock`). The module forms the orchestration layer: it validates inputs, delegates to lower-level indexing code, and returns task IDs for status polling.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository registration and indexing operations |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a threading Lock for repo synchronization |
| `indexer/rest_api.py::TaskStore` | class | In-memory task store with expiration-based cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes empty task dictionary |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks based on current time |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a task with UUID and timestamp, returns ID |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves task by ID from internal dict |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task data and refreshes timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default git branch using git ls-remote |
| `indexer/rest_api.py::_discover_remote_branches` | function | Finds remote branches matching glob via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repositories with JSON persistence |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates temp directory and initializes empty registry |
| `indexer/rest_api.py::RepoRegistry._save` | method | Saves registry dictionary to JSON file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON, validates and detects branches |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds a repo to registry and saves to disk |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repo from registry and saves to disk |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repo data for a given name from registry |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repo names |
| `indexer/rest_api.py::register_repo` | function | Validates URL, clones repo, registers, returns task ID |
| `indexer/rest_api.py::task_status` | function | Returns task status JSON response by task ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repo against indexability criteria, returns report |
| `indexer/rest_api.py::sync_repo` | function | Starts async sync task for a repo, returns task ID |
| `indexer/rest_api.py::rebuild_repo` | function | Starts async rebuild task for a repo, returns task ID |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all remote branches for a repo, returns task ID |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds all remote branches for a repo, returns task ID |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs indexing: parse, cross-ref, density group, upsert vectors, write wiki |
| `indexer/rest_api.py::_run_rebuild_task` | function | Rebuilds repo: removes old data, clones, installs hooks, indexes |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs repo: fetches changes, reindexes modified files, updates manifest |
| `indexer/rest_api.py::_run_register_task` | function | Registers repo with lock acquisition and release |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, discovers branches, injects credentials, stores git config |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repo by name, returns success response |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols using embedded query and call graph expansion, returns JSON |
| `indexer/rest_api.py::trace_call` | function | Traces call chain for a symbol ID, returns JSON with callers and callees |
| `indexer/rest_api.py::get_source_context` | function | Returns source lines around a given position from a file |
| `indexer/rest_api.py::list_repos` | function | Lists all repos with manifest, commit, webhook URL, returns JSON |
| `indexer/rest_api.py::health` | function | Returns health check JSON with OK status |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repo info including file listing and manifest |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates READMEs and skill files from multiple repos into JSON |
| `indexer/rest_api.py::_get_webhook_url` | function | Builds webhook URL with HMAC signature for a repo |
| `indexer/rest_api.py::_webhook_sign` | function | Computes HMAC-SHA256 signature for webhook secret |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook request signature against expected value |
| `indexer/rest_api.py::webhook_by_name` | function | Processes webhook payload, triggers sync or rebuild task |
| `indexer/rest_api.py::create_app` | function | Creates Starlette app with routes, static files, middleware, and registrations |
| `indexer/rest_api.py::_index_page` | function | Serves index HTML page with JSON-replaced environment variables |
| `indexer/rest_api.py::_inject_credentials` | function | Injects username and password into a git remote URL |
| `indexer/rest_api.py::_sanitize_error` | function | Removes sensitive info from error messages for safe logging |
| `indexer/rest_api.py::_store_credentials` | function | Stores git credentials in .git-credentials file with restricted permissions |
| `indexer/rest_api.py::_resolve_repos` | function | Converts repo names to their IDs using registry |
| `indexer/rest_api.py::_trace_call_impl` | function | Traces calls by iterating symbol graph, returns callees and callers |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results by adding call graph neighbors |
| `indexer/rest_api.py::_parse_json_list` | function | Parses JSON string into a list, returns empty on failure |
| `indexer/rest_api.py::_parse_body` | function | Parses request body JSON, returns dict or list |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all branches of registered repos |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all branches of registered repos |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that validates Auth0 JWT tokens on protected routes |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates token for protected paths, returns 401 on failure, else calls next |
## Data Flows
- Client POSTs /register → `register_repo` validates URL → starts `_run_register_task_inner` in executor → clones repo, discovers branches, injects credentials → `RepoRegistry.register` writes JSON → returns task ID
- Client POSTs /sync/<repo> → `sync_repo` → `_run_sync_task` fetches changes via git, reindexes modified files, updates manifest → `TaskStore.update` saves output → returns task ID
- Client POSTs /rebuild/<repo> → `rebuild_repo` → `_run_rebuild_task` removes old data, clones fresh, installs hooks, indexes → returns task ID
- Client GETs /task/<id> → `task_status` → `TaskStore.get` returns JSON with status/detail (or 404 if expired)
## Design Constraints
- Repo operations are serialized per-repo via a threading Lock stored in `_repo_locks` dict – concurrent calls for the same repo will block.
- Tasks are purely in-memory and expire after a fixed duration (removed by `_cleanup` called on each create); there is no persistence of task state across restarts.
- The registry JSON file is stored under a system temp directory, not a configurable path – it may be cleaned by the OS unexpectedly.
- Credentials are injected into the remote URL only during registration (via `_inject_credentials`); they are not stored separately and must be provided again if missing from config.
- All remote branch operations (`sync_all_branches`, `rebuild_all_branches`) first call `_run_register_task_inner` to ensure local tracking refs are up-to-date before iterating branches.
- The `_detect_default_branch` function uses `git ls-remote --symref` and falls back to 'main' or 'master' if detection fails – but only for the configured URL; branch resolution is done at registry load time.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Route, Starlette, StaticFiles, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
- **Imports from:** __future__.annotations, asyncio, collections.defaultdict, datetime.datetime, datetime.timezone, fnmatch, hashlib, hmac, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.utils.load_env_file, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.wiki.IndexEntry, indexer.wiki.build_index, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, json, logging, os, pathlib.Path, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.parse, uuid
## Entry Points
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
