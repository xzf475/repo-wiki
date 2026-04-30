# ./

## Overview

This module implements the REST API layer for an async indexing system that manages per-repo indexing jobs. It converts HTTP requests (register, sync, rebuild, validate) into background tasks tracked via an in-memory `TaskStore` (UUID-keyed, with TTL cleanup). Repo metadata (clone URL, branches, config path) is persisted to a JSON file via `RepoRegistry`, and concurrency is serialized by repo-level `threading.Lock` objects. The API bridges user commands to the indexing pipeline (manifest update, node discovery, vector-upsert) executed in a thread pool executor, enabling non-blocking responses.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repo registration, syncing, and task management |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a threading Lock for repo-level concurrency control |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for tracking async task states with timestamps |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty dict for tasks |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks older than a threshold TTL |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with UUID, runs cleanup, returns task ID |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves a task's status by its ID from the dict |
| `indexer/rest_api.py::TaskStore.update` | method | Updates a task's status and timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch name by running git ls-remote |
| `indexer/rest_api.py::_match_branch_rule` | function | Tests branch name against comma-separated glob patterns using fnmatch |
| `indexer/rest_api.py::_discover_remote_branches` | function | Lists remote branches matching given glob patterns via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Persistent registry mapping repo names to their metadata |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry from a JSON file in temp directory |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry dict to JSON file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON file, detects default branches for each repo |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repo by saving metadata and logging |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repo from registry and saves |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns metadata for a repo name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates metadata fields for a repo, raises ValueError if not found |
| `indexer/rest_api.py::register_repo` | function | Registers a new repo, discovers branches, and creates an initialization task |
| `indexer/rest_api.py::task_status` | function | Returns the status of a task by ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repo configuration and returns any stale or missing files |
| `indexer/rest_api.py::sync_repo` | function | Triggers a sync task for a repo, returns task ID |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers a rebuild task for a repo, returns task ID |
| `indexer/rest_api.py::sync_all_branches` | function | Triggers sync tasks for all discovered branches of a repo |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates repo meta, re-discovers branches, and triggers rebuild |
| `indexer/rest_api.py::rebuild_all_branches` | function | Triggers rebuild tasks for all discovered branches of a repo |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs the full indexing pipeline: manifest update, node discovery, vector upsert |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and runs the inner rebuild task, updates status |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Rebuilds a repo: installs webhook, runs indexing pipeline, saves config |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs a repo: updates manifest, saves config, handles new/changed files |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and runs the inner register task, updates status |
| `indexer/rest_api.py::_run_register_task_inner` | function | Registers repo: stores credentials, discovers branches, saves config |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repo by name and returns success response |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols across repos with query rewriting and call graph expansion |
| `indexer/rest_api.py::trace_call` | function | Traces call graph from a symbol across repos |
| `indexer/rest_api.py::get_source_context` | function | Returns surrounding source lines for a given file and line range |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repos with their metadata and webhook URLs |
| `indexer/rest_api.py::health` | function | Returns health status (number of repos) |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed info for a repo including file tree and collection stats |
| `indexer/rest_api.py::update_repo_meta` | function | Updates metadata for a repo from request body |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates file contents from multiple repos for a skill prompt |
| `indexer/rest_api.py::_get_webhook_url` | function | Generates webhook URL with signed payload for a repo |
| `indexer/rest_api.py::_webhook_sign` | function | Creates HMAC-SHA256 signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook signature using HMAC comparison |
| `indexer/rest_api.py::webhook_by_name` | function | Processes incoming webhook, verifies signature, triggers sync for matching branches |
| `indexer/rest_api.py::create_app` | function | Creates and configures the Starlette application with routes and middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the frontend index.html page or JSON fallback |
| `indexer/rest_api.py::_inject_credentials` | function | Injects username and password into a remote URL |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error message by removing sensitive data |
| `indexer/rest_api.py::_store_credentials` | function | Stores git credentials in a file and sets permissions |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names to metadata dicts from request |
| `indexer/rest_api.py::_trace_call_impl` | function | Traces call graph recursively from a symbol, avoids cycles |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results with call graph ancestors/descendants |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a list, returns empty list on failure |
| `indexer/rest_api.py::_parse_body` | function | Parses request body as JSON or returns dict from form data |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all branches of a repo |
| `indexer/rest_api.py::_rebuild_all` | function |  |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all branches of a repo |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request duration and passes request to next handler |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that verifies JWT token from Authorization header |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks JWT token in Authorization header, returns 401 if invalid |
## Data Flows
- Client POST /repos/register → `register_repo` parses body → discovers remote branches via `_discover_remote_branches` (using git ls-remote) → creates a task in `TaskStore` → runs `_run_indexing_pipeline` in executor → updates task status
- Client POST /repos/:repo/sync → `sync_repo` creates task → acquires repo lock via `_get_repo_lock` → calls `_run_rebuild_task_inner` (webhook install + indexing pipeline + config save) → updates task status
- Client GET /tasks/:id → `task_status` returns task state (status, timestamps) from `TaskStore.get`
- Client POST /repos/:repo/reindex → `reindex_repo` atomically updates repo meta via `RepoRegistry.update_meta` → re-discovers branches → triggers `_run_rebuild_task_inner` in executor
## Design Constraints
- TaskStore._cleanup runs on every create() but uses no locking; concurrent create/update may temporarily see stale or missing tasks
- RepoRegistry stores data in a single JSON file under temp dir; read-modify-write (load, update, _save) is not atomic — concurrent API requests to different repos can corrupt the file
- _get_repo_lock returns a new Lock per repo name but never removes it; memory usage grows with distinct repo names even after unregister
- _run_rebuild_task calls Lock.acquire() without timeout; if the same repo is triggered twice rapidly, the second request blocks indefinitely, potentially hanging the executor thread
- _detect_default_branch silently returns None if git ls-remote fails (e.g. repo unreachable); callers must handle missing default branch gracefully
- Branch pattern matching in _match_branch_rule uses fnmatch on comma-separated globs; patterns are stripped but not validated — malformed globs may match nothing silently
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
