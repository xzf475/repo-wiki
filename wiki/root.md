# ./

## Overview

This module implements the REST API surface for the codebase indexer, exposing endpoints to register, sync, rebuild, validate, and re-index git repositories. It solves the problem of orchestrating long-running indexing pipelines (cloning, parsing, embedding, vector upsert, wiki generation) asynchronously without blocking HTTP handlers. Two key classes – `TaskStore` (in-memory task lifecycle tracker with TTL cleanup) and `RepoRegistry` (persistent on-disk JSON store of repo metadata, lazily auto-detecting default branches) – manage state. Functions like `_run_indexing_pipeline`, `_run_rebuild_task`, and `_run_sync_task` encapsulate the actual indexing logic, while lock acquisition via `_get_repo_lock` prevents concurrent writes to the same repository.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository indexing tasks with TaskStore and RepoRegistry |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a threading.Lock for repo operations |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for async task status and metadata |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty tasks dictionary |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks older than a threshold using time check |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a task with UUID and timestamp, cleans old tasks |
| `indexer/rest_api.py::TaskStore.get` | method | Returns task status dict by task_id or None |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task status and timestamp for a given task_id |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch via git ls-remote on HEAD |
| `indexer/rest_api.py::_discover_remote_branches` | function | Uses git ls-remote to list branches matching a glob |
| `indexer/rest_api.py::RepoRegistry` | class | Manages persistent registry of repositories with metadata |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry storage path in temp directory |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry data to JSON file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from disk, detects default branch if missing |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repo, saves config and logs info |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repo from registry and saves |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repo config dict by name or None |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repo metadata fields; raises ValueError if not found |
| `indexer/rest_api.py::register_repo` | function | Handles registration: clones repo, discovers branches, starts indexing |
| `indexer/rest_api.py::task_status` | function | Returns task status JSON by task_id |
| `indexer/rest_api.py::validate_repo` | function | Validates repo integrity: files, manifest, indexable status |
| `indexer/rest_api.py::sync_repo` | function | Triggers sync task for a repo in background thread |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers rebuild task for a repo in background thread |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all branches of a repo, registers if not present |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, re-discovers branches, rebuilds all |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds all branches of a repo, registers if needed |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs full indexing: parse, embed, upsert vectors, write wiki |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock, runs rebuild inner, releases lock |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Rebuilds repo: clone, install hook, run indexing pipeline |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs repo: fetch, detect stale files, re-index changes |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock, runs register inner, updates status |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, discovers branches, stores credentials, installs hook, indexes |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repo by name and returns success response |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols with query expansion and call graph across repos |
| `indexer/rest_api.py::trace_call` | function | Traces call chain for a symbol across repos |
| `indexer/rest_api.py::get_source_context` | function | Returns source code context lines for a symbol in file |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repos with manifest and commit info |
| `indexer/rest_api.py::health` | function | Returns health check JSON with task store size |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repo info including files and webhook |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repo metadata fields via RepoRegistry |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates files and metadata from multiple repos for skills |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs signed webhook URL for a repo |
| `indexer/rest_api.py::_webhook_sign` | function | Generates HMAC signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies HMAC signature of incoming webhook request |
| `indexer/rest_api.py::webhook_by_name` | function | Handles webhook: verifies signature, triggers sync or register |
| `indexer/rest_api.py::create_app` | function | Builds Starlette app with routes, middleware, static files |
| `indexer/rest_api.py::_index_page` | function | Serves index.html with injected config variables |
| `indexer/rest_api.py::_inject_credentials` | function | Injects credentials into git URL by parsing and encoding |
| `indexer/rest_api.py::_sanitize_error` | function | Strips sensitive info from error messages |
| `indexer/rest_api.py::_store_credentials` | function | Writes git credentials to .git-credentials with restricted permissions |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names to config dicts from registry |
| `indexer/rest_api.py::_trace_call_impl` | function | Recursively traces call graph starting from a symbol |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands symbol list by including callers and callees |
| `indexer/rest_api.py::_parse_json_list` | function | Parses JSON string to list, returns empty on failure |
| `indexer/rest_api.py::_parse_body` | function | Parses request body as JSON, returns dict or raw value |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for a single repo |
| `indexer/rest_api.py::_rebuild_all` | function |  |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for a single repo |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware logging request method, path, duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request info and timing, then calls next |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware validating JWT from Authorization header |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks Authorization header, returns 401 if invalid |
## Data Flows
- Client POST /register -> `register_repo` clones repo, discovers branches, creates async task -> background thread runs `_run_indexing_pipeline` -> TaskStore updated.
- Client POST /sync -> `sync_repo` parses body, creates task -> background thread calls `_run_sync_task` (fetch, detect stale files, re-index) -> TaskStore status updated.
- Client GET /status/{task_id} -> `task_status` returns dict from TaskStore.get or 404 JSON.
- Client POST /reindex -> `reindex_repo` updates meta in RepoRegistry, re-discovers branches, triggers `_run_rebuild_task_inner` per branch atomically.
## Design Constraints
- Each repo gets a dedicated `threading.Lock` via `_get_repo_lock`; concurrent rebuild/sync operations on the same repo are serialized.
- `TaskStore._cleanup` removes tasks older than a hardcoded threshold (checked by `time() - task['timestamp']`), called on every `create`; stale tasks are lost silently.
- If `RepoRegistry._load` finds a repo entry missing the `default_branch` key, it runs `_detect_default_branch` (git ls-remote HEAD) and patches the config before returning – mutation on read.
- `register_repo` appends `/hooks/register` to the repo URL to build a webhook URL – this assumes a specific webhook listener exists at that path.
- `validate_repo` returns a JSON with `is_indexable` only if all files have a manifest entry, no stale files, and the manifest load succeeds; it sums file counts across all entries.
- All async tasks are launched via `run_in_executor` on the event loop's default thread pool executor – no explicit executor management, so thread pool size is system-default.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Route, Starlette, StaticFiles, ValueError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_rebuild_all, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
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
- `reindex_repo`
- `rebuild_all_branches`
- `unregister_repo`
- `list_repos`
- `health`
- `repo_detail`
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
