# indexer/

## Overview

This module provides a REST API to manage the lifecycle of repository indexing, handling registration, sync, rebuild, and validation. It solves the problem of keeping indexed documentation fresh across multiple branches and repositories without blocking the main application. The key classes are `TaskStore` (async task tracking with UUID keys and expiry) and `RepoRegistry` (persistent repo config stored as JSON in a temp directory). The module orchestrates git operations (clone, pull, ls-remote) and indexing pipelines (parse → cross-reference → vectorize → update manifest) as background tasks, exposing status via task IDs.

## Modules
| File | Purpose |
|------|---------|
| indexer/retrieval.py | Functions for symbol search and source context retrieval |
| indexer/rest_api.py | REST API for repository indexing and synchronization tasks |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a lock for a repository using Lock |
| `indexer/rest_api.py::TaskStore` | class | Stores and manages asynchronous tasks with UUID keys |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty task dictionary |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks based on timestamp and max age |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with UUID and adds current timestamp |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves a task dictionary by its ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates a task's fields and refreshes its timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects the default branch name via git ls-remote |
| `indexer/rest_api.py::_discover_remote_branches` | function | Lists remote branches matching a glob pattern using git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Manages a persistent registry of repositories |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates a temporary directory for storing registry data |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes and writes the registry to a JSON file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON file and initializes default branch detection |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a repository by saving config and logging info |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository from the registry and saves |
| `indexer/rest_api.py::RepoRegistry.get` | method | Retrieves a repository's configuration by name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns a sorted list of registered repository names |
| `indexer/rest_api.py::register_repo` | function | Handles POST /register endpoint, clones repo and runs registration task |
| `indexer/rest_api.py::task_status` | function | Returns the current status of an indexing task |
| `indexer/rest_api.py::validate_repo` | function | Validates a repository's manifest and returns status JSON |
| `indexer/rest_api.py::sync_repo` | function | Queues a sync task for a specific repository branch |
| `indexer/rest_api.py::rebuild_repo` | function | Queues a rebuild task for a specific repository branch |
| `indexer/rest_api.py::sync_all_branches` | function | Queues sync tasks for all branches of a repository |
| `indexer/rest_api.py::rebuild_all_branches` | function | Queues rebuild tasks for all branches of a repository |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes indexing pipeline: parse, cross-reference, vectorize, update |
| `indexer/rest_api.py::_run_rebuild_task` | function | Rebuilds a repository by cloning fresh and re-indexing |
| `indexer/rest_api.py::_run_sync_task` | function | Pulls latest changes and updates the index incrementally |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock and runs the inner registration task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, stores credentials, configures and runs initial index |
| `indexer/rest_api.py::unregister_repo` | function | Handles DELETE endpoint to unregister a repository |
| `indexer/rest_api.py::search_symbols` | function | Searches code symbols by name or embedding query |
| `indexer/rest_api.py::trace_call` | function | Returns call graph trace for a given symbol |
| `indexer/rest_api.py::get_source_context` | function | Retrieves source code lines around a given symbol |
| `indexer/rest_api.py::list_repos` | function | Returns a JSON list of all registered repositories |
| `indexer/rest_api.py::health` | function | Returns a simple health check JSON response |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed information about a specific repository |
| `indexer/rest_api.py::multi_repo_skill` | function | Executes a skill across multiple repositories and returns results |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs a signed webhook URL for repository events |
| `indexer/rest_api.py::_webhook_sign` | function | Signs a webhook payload using HMAC-SHA256 |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies an incoming webhook signature against expected |
| `indexer/rest_api.py::webhook_by_name` | function | Processes incoming webhook for a named repository |
| `indexer/rest_api.py::create_app` | function | Builds and configures the Starlette ASGI application |
| `indexer/rest_api.py::_index_page` | function | Returns the main HTML page with embedded config data |
| `indexer/rest_api.py::_inject_credentials` | function | Inserts username/password into a git remote URL |
| `indexer/rest_api.py::_sanitize_error` | function | Removes credential strings from error messages |
| `indexer/rest_api.py::_store_credentials` | function | Saves git credentials in the repo's .git-credentials file |
| `indexer/rest_api.py::_resolve_repos` | function | Converts repository names or wildcards to list of configs |
| `indexer/rest_api.py::_trace_call_impl` | function | Recursively builds call graph for a symbol |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Augments search results with symbols from call graph |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a Python list |
| `indexer/rest_api.py::_parse_body` | function | Parses request body, returning dict or falling back to form |
| `indexer/rest_api.py::_run_all` | function | Runs sync task on all branches |
| `indexer/rest_api.py::_run_all` | function | Runs sync task on all branches |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request timing and info |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request start and duration, then calls next middleware |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that verifies authentication tokens |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates Authorization header and rejects unauthenticated requests |
| `indexer/retrieval.py::search_symbols` | function | Searches symbols in the retrieval index using embeddings |
| `indexer/retrieval.py::trace_call` | function | Builds call graph for a symbol in retrieval context |
| `indexer/retrieval.py::get_source_context` | function | Retrieves source code lines around a symbol from files |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Expands a set of symbols by following call graph edges |
| `indexer/retrieval.py::_parse_json_list` | function | Parses a JSON string into a list of objects |
## Data Flows
- POST /register → `register_repo` creates a TaskStore task → `_run_register_task_inner` clones repo, stores credentials, runs initial index → task status pollable via GET /task/{id}
- POST /sync → `sync_repo` queues task → `_run_sync_task` pulls latest changes, detects stale files, increments index → updates tracked files list
- POST /rebuild → `rebuild_repo` queues task → `_run_rebuild_task` deletes local clone, re-clones, runs full indexing pipeline
- GET /validate → `validate_repo` loads manifest, checks all tracked files exist, returns coverage stats
## Design Constraints
- A per-repo lock (via `_get_repo_lock`) prevents concurrent register/sync/rebuild operations on the same repo; the lock must be explicitly acquired and released in each task function.
- `TaskStore._cleanup` is called on every `create()`, removing stale tasks older than max age; callers must not rely on tasks persisting indefinitely.
- `RepoRegistry` stores data in a temporary directory (`gettempdir`), so registry is ephemeral across restarts unless persisted elsewhere.
- Default branch detection and remote branch listing use `git ls-remote`; they may fail or return empty for repositories without remotes or with authentication issues.
- Unregister (`unregister_repo`) only removes the entry from `RepoRegistry`; it does not delete indexed data or the local clone (that is left to a separate cleanup or subsequent rebuild).
- Validation computes tracked file counts from `all_tracked_files` and sums file counts from manifest; missing files are reported but not automatically fixed.
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
