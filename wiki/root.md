# ./

## Overview

This module implements the HTTP API for managing repository indexing operations. It defines `TaskStore` (an in-memory store for tracking async indexing tasks with expiration-based cleanup) and `RepoRegistry` (a persistent JSON file that holds repository configurations including clone URLs and default branches). The API endpoints (`register_repo`, `sync_repo`, `rebuild_repo`, `unregister_repo`, `search_symbols`) allow clients to trigger long-running indexing pipelines, each guarded by a per-repo threading lock to prevent concurrent index mutations. The module coordinates with lower-level parsing, enrichment, vector storage, and wiki writing components via the `_run_indexing_pipeline` function, which is called inside executor tasks for asynchronous execution.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository indexing and management |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires and returns a threading Lock for repo synchronization |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for indexing task states with expiration cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty dictionary to hold tasks |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks whose creation time exceeds the timeout threshold |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task, assigns UUID, records creation time, cleans up stale tasks |
| `indexer/rest_api.py::TaskStore.get` | method | Returns the task dictionary for the given task ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates an existing task with new data and refreshes its timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Runs `git symbolic-ref` to detect the default branch name |
| `indexer/rest_api.py::RepoRegistry` | class | Persistent registry of registered repositories stored as JSON file |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry storage path in temp directory and loads existing data |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes the registry dictionary to JSON and writes to file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Reads JSON file, validates entries, detects default branches, returns registry dict |
| `indexer/rest_api.py::RepoRegistry.register` | method | Loads config, adds repo entry to registry, serializes and saves |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repo entry from the registry and saves the updated data |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns the configuration dictionary for the given repo name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns a sorted list of all registered repository names |
| `indexer/rest_api.py::register_repo` | function | Parses request body, creates register task, runs register pipeline asynchronously |
| `indexer/rest_api.py::task_status` | function | Returns the task data for the given task ID from TaskStore |
| `indexer/rest_api.py::validate_repo` | function | Checks repo structure, counts staled/staged files, returns validation results |
| `indexer/rest_api.py::sync_repo` | function | Creates a sync task and runs sync pipeline asynchronously for the repo |
| `indexer/rest_api.py::rebuild_repo` | function | Creates a rebuild task and runs rebuild pipeline asynchronously for the repo |
| `indexer/rest_api.py::sync_all_branches` | function | Creates sync tasks for all branches and runs each sync pipeline asynchronously |
| `indexer/rest_api.py::rebuild_all_branches` | function | Creates rebuild tasks for all branches and runs each rebuild pipeline asynchronously |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs the full indexing pipeline: cross-reference, enrich, write wiki and vectors |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock, clears existing index, reinstalls hooks, runs full indexing pipeline |
| `indexer/rest_api.py::_run_sync_task` | function | Acquires lock, processes changed files, updates index and manifest incrementally |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock, runs inner register task, releases lock |
| `indexer/rest_api.py::_run_register_task_inner` | function | Injects credentials, installs hooks, detects branches, saves config and registers |
| `indexer/rest_api.py::unregister_repo` | function | Parses body, removes repo from registry, returns success response |
| `indexer/rest_api.py::search_symbols` | function | Parses query, performs vector search, expands results with call graph, returns sorted symbols |
| `indexer/rest_api.py::trace_call` | function | Resolves repos, traces call graph for given symbol, returns expanded list |
| `indexer/rest_api.py::get_source_context` | function | Reads file, extracts context lines around given line range, returns JSON |
| `indexer/rest_api.py::list_repos` | function | Lists repos with manifest info, commit counts, and webhook URLs |
| `indexer/rest_api.py::health` | function | Returns a JSON response indicating number of registered repos |
| `indexer/rest_api.py::repo_detail` | function | Returns manifest, file counts, webhook URL, and index files for a repo |
| `indexer/rest_api.py::multi_repo_skill` | function | Collects skill files from multiple repos, returns merged JSON list |
| `indexer/rest_api.py::_get_webhook_url` | function | Builds webhook URL with HMAC signature from repo config |
| `indexer/rest_api.py::_webhook_sign` | function | Computes HMAC-SHA256 hex digest of payload using secret key |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Compares computed HMAC signature with provided signature using constant-time compare |
| `indexer/rest_api.py::webhook_by_name` | function | Verifies signature, triggers sync task for repo on webhook event |
| `indexer/rest_api.py::create_app` | function | Sets up routes, middleware, static files, and returns the ASGI app |
| `indexer/rest_api.py::_index_page` | function | Reads index.html, inlines repo list as JSON, returns HTML response |
| `indexer/rest_api.py::_inject_credentials` | function | Adds username and password to repo URL for authentication |
| `indexer/rest_api.py::_sanitize_error` | function | Replaces credentials and URLs in error strings with sanitized placeholders |
| `indexer/rest_api.py::_store_credentials` | function | Stores remote credentials in repo's git config as credential helper |
| `indexer/rest_api.py::_resolve_repos` | function | Returns list of repo names from request body or all registered names |
| `indexer/rest_api.py::_trace_call_impl` | function | Recursively follows calls from a starting symbol using call graph data |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Adds callers/callees to search results based on call graph adjacency |
| `indexer/rest_api.py::_parse_json_list` | function | Loads a JSON string and returns a list, handling single-object lists |
| `indexer/rest_api.py::_parse_body` | function | Returns JSON-decoded body or empty dict if not JSON |
| `indexer/rest_api.py::_run_all` | function |  |
| `indexer/rest_api.py::_run_all` | function |  |
| `indexer/rest_api.py::_AuthMiddleware` | class | Starlette middleware that checks Authorization header for allowed access |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates token from Authorization header, returns 401 if invalid |
## Data Flows
- client POST /register → `register_repo` creates a task, executes `_run_register_task_inner` (inject credentials, install hooks, detect branches, save registry) then runs `_run_indexing_pipeline` (cross-ref, enrich, write wiki/vectors).
- client POST /sync → `sync_repo` creates a task, executes `_run_sync_task` (acquires per-repo lock, processes changed files via git diff, incrementally updates index entries and manifest).
- client POST /search → `search_symbols` parses query, performs vector search, expands results with call graph, returns sorted symbol list.
- client POST /unregister → `unregister_repo` removes the repo entry from `RepoRegistry` (no cleanup of indexed data).
## Design Constraints
- Each repository has a `threading.Lock` acquired before any mutation (register, sync, rebuild) to prevent concurrent writes; `_get_repo_lock` lazily creates these locks.
- `TaskStore._cleanup` removes tasks whose creation time exceeds a timeout threshold (not a fixed count limit), and only runs on `create()`, keeping the store lean.
- `RepoRegistry._load` validates each entry is a dict with a `clone_url` key; it calls `_detect_default_branch` to auto-populate missing branch info from git.
- `_run_sync_task` handles incremental updates by processing only changed files (e.g., via git diff) and uses `IndexEntry` with `removesuffix` to handle renames/moves.
- Credentials are stored separately (via `_store_credentials` and `_inject_credentials`) and are not part of the registry JSON, preventing credential leakage in the file.
- Unregister does not remove previously indexed data; the underlying wiki pages and vectors persist until a rebuild or manual cleanup.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Route, Starlette, StaticFiles, _cleanup, _detect_default_branch, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, exists, extend, get, get_by_ids, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
- **Imports from:** __future__.annotations, asyncio, collections.defaultdict, datetime.datetime, datetime.timezone, hashlib, hmac, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.utils.load_env_file, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.wiki.IndexEntry, indexer.wiki.build_index, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, json, logging, os, pathlib.Path, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.parse, uuid
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
