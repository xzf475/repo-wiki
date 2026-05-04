# ./

## Overview

This module implements the REST API layer for a codebase indexing service. It orchestrates asynchronous operations (clone, index, sync, rebuild) for multiple repositories, using an in-memory `TaskStore` with a 10-minute TTL to track request progress and a `RepoRegistry` persisted as JSON for tracking registered repositories and their metadata. It integrates with git commands for branch discovery, pattern-based branch filtering, and lock acquisition (`_get_repo_lock`) to prevent concurrent operations on the same repo. The module serves as the entry point for external clients and the glue between HTTP requests and the internal indexing pipeline (enrichment, file tracking, density grouping, manifest handling).

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST endpoints for repo registration, indexing, and task status |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a named Lock for a repository. |
| `indexer/rest_api.py::TaskStore` | class | In-memory dictionary store for tasks with time-based cleanup. |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes the TaskStore with an empty tasks dictionary. |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks older than 10 minutes from the store. |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with UUID and timestamp, then cleans up. |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves a task by its unique identifier. |
| `indexer/rest_api.py::TaskStore.update` | method | Updates a task's status and timestamp. |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch name via git commands. |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks branch name against comma-separated glob patterns. |
| `indexer/rest_api.py::_discover_remote_branches` | function | Finds remote branches matching glob patterns using git ls-remote. |
| `indexer/rest_api.py::RepoRegistry` | class | Persists repository registration info in a JSON file. |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Sets up registry with a temporary JSON file path. |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry to JSON file. |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON, detects default branches. |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds a repo to registry and saves. |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repo from registry and saves. |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository info dict by name. |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names. |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repo metadata and saves. |
| `indexer/rest_api.py::register_repo` | function | Clones repo, discovers branches, creates indexing task. |
| `indexer/rest_api.py::task_status` | function | Returns task status as JSON. |
| `indexer/rest_api.py::validate_repo` | function | Validates repo health by checking files and manifest. |
| `indexer/rest_api.py::sync_repo` | function | Syncs repo by running sync pipeline as background task. |
| `indexer/rest_api.py::rebuild_repo` | function | Rebuilds repo index by running rebuild pipeline. |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all branches by discovering and syncing each. |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, discovers branches, rebuilds all. |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds all branches of a repository. |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs full indexing: enrichment, file tracking, density. |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock and runs rebuild inner task. |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Performs full rebuild: clone, manifest, indexing. |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs repo: fetch, build index, run pipeline. |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock and runs register inner task. |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, stores credentials, runs indexing. |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repo from the registry. |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols using embeddings, expands via call graph. |
| `indexer/rest_api.py::trace_call` | function | Traces call chains starting from a symbol. |
| `indexer/rest_api.py::get_source_context` | function | Retrieves source lines around a given line. |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repos with metadata. |
| `indexer/rest_api.py::health` | function | Returns a health check JSON response. |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed info about a repo. |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repo metadata fields. |
| `indexer/rest_api.py::multi_repo_skill` | function | Lists skills across repos based on file patterns. |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook URL for a repo. |
| `indexer/rest_api.py::_webhook_sign` | function | Generates HMAC signature for webhook. |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook request signature. |
| `indexer/rest_api.py::webhook_by_name` | function | Handles webhook events: verify, trigger sync. |
| `indexer/rest_api.py::create_app` | function | Creates Starlette app with routes and middleware. |
| `indexer/rest_api.py::_index_page` | function | Serves the index.html frontend page. |
| `indexer/rest_api.py::_inject_credentials` | function | Embeds credentials into Git remote URL. |
| `indexer/rest_api.py::_sanitize_error` | function | Removes sensitive info from error strings. |
| `indexer/rest_api.py::_store_credentials` | function | Stores Git credentials for authentication. |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names to config dictionaries. |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements call trace by fetching symbol definitions. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands results with transitive call graph. |
| `indexer/rest_api.py::_parse_json_list` | function | Parses JSON string into a list. |
| `indexer/rest_api.py::_parse_body` | function | Parses request body as JSON dictionary. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task for a repository. |
| `indexer/rest_api.py::_rebuild_all` | function | Updates and runs rebuild inner task. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task for a repository. |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request method and path. |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Intercepts request, logs, calls next middleware. |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that validates Auth0 JWT tokens. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Intercepts and validates auth for incoming requests, proceeds or returns error |
## Data Flows
- Client POST /register_repo → clones repo via `register_repo`, discovers branches via `_discover_remote_branches`, creates task in `TaskStore`, runs indexing pipeline in executor, updates `RepoRegistry`.
- Client POST /sync_repo → parses body, creates task in `TaskStore`, runs sync pipeline in executor, registers updated repo info, returns task ID.
- Client POST /reindex_repo → updates repo meta via `update_meta`, discovers new branches, calls `_run_rebuild_task_inner` for each branch (clone, manifest, indexing), creates tracking tasks.
- Client GET /task_status?id=X → retrieves task state from `TaskStore` (in-memory, may return None after 10 min).
## Design Constraints
- TaskStore is in-memory only; tasks older than 10 minutes are removed during `create()` — no persistence across app restarts.
- RepoRegistry persists to a temporary JSON file by default (`tempfile.gettempdir()`), not suitable for permanent storage without configuration.
- Branch discovery uses `git ls-remote` (requires network) and matches patterns via `fnmatch`; only remote branches are considered, not local.
- Concurrent operations on the same repo are serialized using a named lock (`_get_repo_lock`), likely `threading.Lock` or `multiprocessing.Lock`, preventing race conditions in pipelines.
- `_run_rebuild_task_inner` checks for an existing Git repo (`is_git_repo`) before cloning and deletes stale files based on manifest tracking.
- `validate_repo` side-effect-free: it reads files and manifest but never modifies state; it returns a JSON health report.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, PersistentClient, Route, Starlette, StaticFiles, ValueError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _match_branch_rule, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, any, append, body, bool, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, count, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_or_create_collection, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_dir, is_git_repo, is_relative_to, isinstance, items, iter, iterdir, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
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
