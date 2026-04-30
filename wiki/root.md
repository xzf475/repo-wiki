# ./

## Overview

This module exposes the REST API for the code indexer service, enabling remote management of repository indexing operations. It provides endpoints to register/unregister repos, trigger sync or full rebuilds, and query async task progress. Two key classes support this: `TaskStore` manages in-memory task records with automatic expiry, and `RepoRegistry` persists repo metadata (including branch rules and webhook config) to a JSON file. The module orchestrates git operations (remote branch discovery via ls-remote, default branch detection) and the vector indexing pipeline, all executed as background tasks protected by file-level locks to prevent races.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository indexing and syncing tasks |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a lock for the given repository path using Lock. |
| `indexer/rest_api.py::TaskStore` | class | Stores and manages asynchronous task records with timestamps. |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty dictionary to hold tasks. |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks from the store based on current time. |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with a UUID, cleans up expired tasks first. |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves a task by its identifier from the store. |
| `indexer/rest_api.py::TaskStore.update` | method | Updates a task's payload and timestamp, returns the updated task. |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects the default branch of a git repository using git commands. |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks if a branch name matches a comma-separated glob pattern via fnmatch. |
| `indexer/rest_api.py::_discover_remote_branches` | function | Discovers remote branches matching glob patterns using git ls-remote. |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registration, persistence, and lookup of repository metadata. |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes the registry with a file path in the temp directory. |
| `indexer/rest_api.py::RepoRegistry._save` | method | Saves the registry dictionary to a JSON file on disk. |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON file, detects default branch if needed. |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repository, saves registry, and loads its config. |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Unregisters a repository by name and saves the updated registry. |
| `indexer/rest_api.py::RepoRegistry.get` | method | Retrieves a repository entry by its name from the registry. |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns a sorted list of all registered repository names. |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repository metadata, raises ValueError if not found, then saves. |
| `indexer/rest_api.py::register_repo` | function | Registers a new repository, discovers branches, creates webhook, returns task. |
| `indexer/rest_api.py::task_status` | function | Returns the status and result of a given task by ID. |
| `indexer/rest_api.py::validate_repo` | function | Validates repository configuration, manifest, and file index status. |
| `indexer/rest_api.py::sync_repo` | function | Triggers an incremental sync task for a repository's default branch. |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers a full rebuild task for a repository's default branch. |
| `indexer/rest_api.py::sync_all_branches` | function | Discovers and syncs all remote branches of a repository. |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates repo meta, re-discovers branches, and rebuilds all index. |
| `indexer/rest_api.py::rebuild_all_branches` | function | Discovers and rebuilds the index for all remote branches of a repo. |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes the indexing pipeline: batch, embed, upsert vectors to store. |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and runs the rebuild task inner function. |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Performs full rebuild: loads config, creates manifest, runs indexing pipeline. |
| `indexer/rest_api.py::_run_sync_task` | function | Performs incremental sync: detects changed files, updates index. |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and runs the registration task inner function. |
| `indexer/rest_api.py::_run_register_task_inner` | function | Performs registration: discovers branches, syncs initial index, sets webhook. |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository and returns success response. |
| `indexer/rest_api.py::search_symbols` | function | Searches for symbols across repositories using query and call graph expansion. |
| `indexer/rest_api.py::trace_call` | function | Traces the call graph for a given symbol across repositories. |
| `indexer/rest_api.py::get_source_context` | function | Retrieves source code context lines around a given symbol location. |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repositories with webhook, branch, and index info. |
| `indexer/rest_api.py::health` | function | Returns a health check response with current task count. |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed information about a repository including collections. |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repository metadata fields from request body. |
| `indexer/rest_api.py::multi_repo_skill` | function | Generates multi-repo skill definitions combining manifests from registered repos. |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs the webhook URL for a repository with a signature. |
| `indexer/rest_api.py::_webhook_sign` | function | Creates an HMAC-SHA256 signature for webhook URL authentication. |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies an incoming webhook signature against the expected HMAC. |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook events, triggers sync or rebuild based on branch. |
| `indexer/rest_api.py::create_app` | function | Creates the Starlette ASGI application with all routes, middleware, and static files. |
| `indexer/rest_api.py::_index_page` | function | Serves the dashboard index HTML page or returns JSON status. |
| `indexer/rest_api.py::_inject_credentials` | function | Injects username and password into a repository URL for git access. |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error messages by removing sensitive information. |
| `indexer/rest_api.py::_store_credentials` | function | Stores git credentials in a local file with restricted permissions. |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repository names from request data or returns all registered repos. |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements call graph traversal to trace all callers of a symbol. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results by including symbols from the call graph. |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON list string into a Python list, handles errors. |
| `indexer/rest_api.py::_parse_body` | function | Parses the request body as JSON, returns dict or list based on content. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task across all repositories. |
| `indexer/rest_api.py::_rebuild_all` | function | Runs rebuild task inner for all repositories, updating status. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task across all repositories. |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request duration and method. |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Dispatches the request and logs method, path, and duration. |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that verifies authentication token for protected routes. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates bearer token, returns 401 if invalid, else calls next. |
## Data Flows
- Client POSTs to register_repo → parses body → validates → registers via RepoRegistry → discovers branches → creates webhook → creates async task → returns task ID
- Client GETs task_status → looks up task ID in TaskStore → returns status/result or 404
- Client POSTs to rebuild_all_branches → discovers remote branches matching globs → for each branch creates a rebuild task via _run_rebuild_task → each task acquires repo lock → runs _run_rebuild_task_inner (config load, manifest creation, indexing pipeline)
- Client POSTs to reindex_repo → updates meta via RepoRegistry.update_meta → re-discovers branches → creates rebuild tasks for all branches (similar lock + pipeline)
## Design Constraints
- TaskStore.create() triggers _cleanup every time, removing tasks older than the expiry threshold (defined elsewhere but checked via `time` comparisons); no explicit expiry configuration is exposed via this module.
- RepoRegistry persists to a single JSON file under `os.tempdir`; the file is loaded on init and saved after every mutation (register, unregister, update_meta) — concurrent processes could race on the same file.
- _run_rebuild_task acquires a per-repo lock via `Lock` to serialize rebuilds of the same repo; the lock is released manually after the inner function completes, and the task status is updated atomically within the lock scope.
- _discover_remote_branches uses `git ls-remote` and filters via `fnmatch` with comma-separated glob patterns from repo config; empty glob list means no branches are processed, not all branches.
- validate_repo depends on external functions (`load_manifest`, `all_tracked_files`, `stale_files`, `sanitize_group_label`) that may raise or return empty results; the endpoint assembles a JSON response string directly, not a structured error.
- All blocking operations (git commands, pipeline) are offloaded to a thread pool via `loop.run_in_executor` using the current running asyncio loop; this assumes the FastAPI app runs in a loop that supports `get_running_loop()`.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, PersistentClient, Route, Starlette, StaticFiles, ValueError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _match_branch_rule, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, any, append, body, bool, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, count, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_or_create_collection, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_rebuild_all, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
- **Imports from:** __future__.annotations, asyncio, chromadb.PersistentClient, collections.defaultdict, datetime.datetime, datetime.timezone, fnmatch, hashlib, hmac, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.utils.load_env_file, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.wiki.IndexEntry, indexer.wiki.build_index, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, json, logging, os, pathlib.Path, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.parse, uuid
## Entry Points
- `TaskStore`
- `RepoRegistry`
- `register_repo`
- `task_status`
- `validate_repo`
- `sync_repo`
- `rebuild_repo`
- `sync_all_branches`
- `reindex_repo`
- `rebuild_all_branches`
- `unregister_repo`
- `list_repos`
- `health`
- `repo_detail`
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
