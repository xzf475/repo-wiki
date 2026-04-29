# ./

## Overview

This module implements REST API endpoints for managing repository indexing operations (register, sync, rebuild, validate, status). It solves the problem of coordinating long-running git-based indexing tasks asynchronously while providing polling-based task status. The core classes are TaskStore (in-memory task tracking with expiry-based cleanup) and RepoRegistry (persistent JSON-backed repository metadata store, including auto-detected default branch). Endpoints dispatch work to background executor threads using file-based per-repo locks (_get_repo_lock) to prevent concurrent operations on the same repository, and leverage git ls-remote to discover remote branches for branch-level sync/rebuild.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository registration and indexing tasks |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a file-based lock for a repository. |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for tracking async indexing tasks. |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty task dictionary. |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks from the store. |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with a unique ID and records timestamp. |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves a task's status by its ID. |
| `indexer/rest_api.py::TaskStore.update` | method | Updates a task's status and timestamp. |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects the default branch name using git ls-remote. |
| `indexer/rest_api.py::_discover_remote_branches` | function | Discovers remote branches matching a glob pattern via git ls-remote. |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repositories and their metadata. |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry with a temp directory path. |
| `indexer/rest_api.py::RepoRegistry._save` | method | Persists the registry to a JSON file. |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads and validates registry from JSON, detects default branches. |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repository after loading its config. |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository from the registry. |
| `indexer/rest_api.py::RepoRegistry.get` | method | Retrieves a repo's metadata by name. |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names. |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates metadata for a specific repository. |
| `indexer/rest_api.py::register_repo` | function | Registers a repository by cloning and setting up webhooks. |
| `indexer/rest_api.py::task_status` | function | Returns the status of a given indexing task. |
| `indexer/rest_api.py::validate_repo` | function | Validates a repository's indexability and file consistency. |
| `indexer/rest_api.py::sync_repo` | function | Triggers an async sync task for a repository. |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers an async rebuild task for a repository. |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all branches of a repository asynchronously. |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds all branches of a repository asynchronously. |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes the full indexing pipeline: parse, embed, write. |
| `indexer/rest_api.py::_run_rebuild_task` | function | Rebuilds a repository by cloning and reindexing all files. |
| `indexer/rest_api.py::_run_sync_task` | function | Incrementally syncs a repository by detecting changed files. |
| `indexer/rest_api.py::_run_register_task` | function | Runs registration task with a repository lock. |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, indexes, installs webhook, and stores credentials. |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository and returns success response. |
| `indexer/rest_api.py::search_symbols` | function | Searches for symbols across repositories with query expansion. |
| `indexer/rest_api.py::trace_call` | function | Traces call graph starting from a given symbol. |
| `indexer/rest_api.py::get_source_context` | function | Retrieves source code context lines for a symbol. |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repositories with their metadata. |
| `indexer/rest_api.py::health` | function | Returns a simple health check response. |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed information about a repository. |
| `indexer/rest_api.py::update_repo_meta` | function | Updates metadata for a repository via API. |
| `indexer/rest_api.py::multi_repo_skill` | function | Returns aggregated skill definitions across multiple repositories. |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs a signed webhook URL for a repository. |
| `indexer/rest_api.py::_webhook_sign` | function | Signs a webhook URL using HMAC SHA256. |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies a webhook signature against the expected value. |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook events, triggers indexing tasks. |
| `indexer/rest_api.py::create_app` | function | Creates the Starlette application with routes and middleware. |
| `indexer/rest_api.py::_index_page` | function | Serves the static index HTML page with dynamic config. |
| `indexer/rest_api.py::_inject_credentials` | function | Injects credentials into a git remote URL. |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error messages by removing sensitive info. |
| `indexer/rest_api.py::_store_credentials` | function | Stores git credentials in a temporary file. |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repository names to their configurations. |
| `indexer/rest_api.py::_trace_call_impl` | function | Computes transitive call graph starting from a symbol. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands a set of symbols with their call graph. |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a Python list. |
| `indexer/rest_api.py::_parse_body` | function | Parses a request body from JSON or string. |
| `indexer/rest_api.py::_run_all` | function | Runs a per-branch sync or rebuild task for all branches. |
| `indexer/rest_api.py::_run_all` | function | Runs a per-branch sync or rebuild task for all branches. |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request duration. |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request method, path, and response status with duration. |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that verifies authentication tokens. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates bearer token or allows public paths, rejects unauthorized. |
## Data Flows
- Client POST /register → register_repo creates TaskStore task → _run_register_task acquires repo lock → _run_register_task_inner clones repo, indexes, installs webhook, stores credentials → task updated to 'completed' or 'error'
- Client POST /sync/{name} → sync_repo creates TaskStore task → _run_sync_task acquires repo lock → detects changed files since last sync via git diff → runs indexing pipeline on changed files → updates manifest
- Client POST /rebuild/{name} → rebuild_repo creates TaskStore task → _run_rebuild_task acquires repo lock → re-clones repo, indexes all indexable files from scratch → updates manifest and webhook
- Client POST /sync-all-branches → sync_all_branches discovers remote branches via ls-remote glob → for each branch creates a sync task (no locking across branches; per-branch lock within each _run_sync_task)
## Design Constraints
- TaskStore._cleanup keeps only the most recent 100 tasks (sorted by timestamp, old ones pruned) – runs on every create() call
- RepoRegistry._load calls _detect_default_branch (git ls-remote network call) for every registered repo on every load – expensive for many repos
- File lock per repo is acquired by name derivation from repo URL/name – prevents concurrent register/sync/rebuild on same repo but not across branches (per-branch lock implied but not shown)
- validate_repo checks all files in the manifest with _is_indexable, but also fails if the manifest file itself does not exist on disk – not just validation of index content
- _discover_remote_branches uses fnmatch glob pattern on ref names from ls-remote; matching is case-sensitive on the remote ref string
- TaskStore uses a simple dict and relies on caller to call update() from background tasks; there is no persistence, so task statuses are lost on server restart
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Route, Starlette, StaticFiles, ValueError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
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
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
