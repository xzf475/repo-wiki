# indexer/

## Overview

This module implements a RESTful indexer service that manages the lifecycle of code repositories: registration, synchronous/rebuild indexing, and validation. It solves the problem of orchestrating long-running, resource-intensive indexing pipelines (clone, describe, enrich, embed, write pages) while providing asynchronous task tracking via an in-memory `TaskStore` with expiration cleanup. The `RepoRegistry` persists repository metadata to a temp JSON file, enabling fault-tolerant re-registration. Core operations (`_run_register_task`, `_run_sync_task`, `_run_rebuild_task`) enforce per-repo locking with `_get_repo_lock` to prevent concurrent modifications. This service is the entry point for the broader indexing system, separating HTTP concerns from the actual indexing logic (presumably in `retrieval.py`).

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository registration and indexing tasks |
| indexer/retrieval.py | Code symbol search and source context retrieval |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a lock for the given repository |
| `indexer/rest_api.py::TaskStore` | class | Manages in-memory task storage with expiration cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty task dictionary |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks that have exceeded their time-to-live |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with unique UUID and timestamp |
| `indexer/rest_api.py::TaskStore.get` | method | Returns the task object for a given task ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task attributes and refreshes the timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch name using git command output |
| `indexer/rest_api.py::_discover_remote_branches` | function | Uses git ls-remote to find remote branches matching a glob pattern |
| `indexer/rest_api.py::RepoRegistry` | class | Persistent registry of repositories with load/save to disk |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates temp directory for registry storage file |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry data to a JSON file on disk |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from disk, migrates legacy entries, detects default branch |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds a new repository entry and saves registry |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository entry and saves registry |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository entry by name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names |
| `indexer/rest_api.py::register_repo` | function | Registers a new repository, clones it, and starts indexing |
| `indexer/rest_api.py::task_status` | function | Returns JSON response with task status for given task ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repository structure and returns validation result |
| `indexer/rest_api.py::sync_repo` | function | Starts an async task to sync repository with its remote |
| `indexer/rest_api.py::rebuild_repo` | function | Starts an async task to rebuild repository index from scratch |
| `indexer/rest_api.py::sync_all_branches` | function | Starts sync tasks for all remote branches of a repository |
| `indexer/rest_api.py::rebuild_all_branches` | function | Starts rebuild tasks for all remote branches of a repository |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs full indexing pipeline: describe, enrich, embed, and write pages |
| `indexer/rest_api.py::_run_rebuild_task` | function | Executes rebuild task: clone repo, run indexing pipeline, save config |
| `indexer/rest_api.py::_run_sync_task` | function | Executes sync task: pull changes, update index, and save config |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock and runs inner registration task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, indexes, and registers it; handles errors |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository and returns JSON response |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols using query expansion and call graph; returns results |
| `indexer/rest_api.py::trace_call` | function | Traces call graph for a given symbol across repos |
| `indexer/rest_api.py::get_source_context` | function | Returns source code context lines for a symbol |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repositories with their metadata and webhook URL |
| `indexer/rest_api.py::health` | function | Returns JSON health check response |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed information about a specific repository |
| `indexer/rest_api.py::multi_repo_skill` | function | Performs a multi-repository skill query and returns combined results |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook URL with signature for a repository |
| `indexer/rest_api.py::_webhook_sign` | function | Computes HMAC-SHA256 signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook signature using constant-time comparison |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook events, verifies signature, triggers sync/rebuild |
| `indexer/rest_api.py::create_app` | function | Creates and configures the Starlette app with routes and middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the main HTML index page with dynamic content |
| `indexer/rest_api.py::_inject_credentials` | function | Injects credentials (username/password) into a repository URL |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error messages by removing sensitive information |
| `indexer/rest_api.py::_store_credentials` | function | Stores repository credentials securely in git config |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves list of repositories from request parameters |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements call graph tracing: expands symbols and builds call tree |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands symbols by adding those reachable via call graph |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a Python list |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body, handling bytes or dict inputs |
| `indexer/rest_api.py::_run_all` | function | Wraps _run_rebuild_task for all branches |
| `indexer/rest_api.py::_run_all` | function | Wraps _run_rebuild_task for all branches |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request duration and method |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request start time and duration after response |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that validates JWT tokens for protected routes |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates JWT from Authorization header, returns 401 if invalid |
| `indexer/retrieval.py::search_symbols` | function | Searches symbols using vector embeddings and call graph expansion |
| `indexer/retrieval.py::trace_call` | function | Traces call graph for a symbol, returning a list of symbol IDs |
| `indexer/retrieval.py::get_source_context` | function | Returns source code context lines for a given symbol |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Expands symbol set by following call graph edges |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON string into a list, handling quoted strings |
## Data Flows
- register_repo → _run_register_task_inner → clone repo → _run_indexing_pipeline (describe, enrich, embed, write) → save config → unlock
- sync_repo → _run_sync_task → pull remote changes → update IndexEntry → save config → unlock
- rebuild_repo → _run_rebuild_task → rmtree local clone → re-clone → _run_indexing_pipeline → save config → unlock
- validate_repo → load_manifest → check sanitize_group_label → count modified files → return JSON result
## Design Constraints
- Per-repo lock acquired via `_get_repo_lock` (a `Lock` per repo name); two operations on the same repo will be serialized, but different repos can run concurrently.
- `TaskStore` is purely in-memory and tasks expire after a hardcoded TTL (checked in `_cleanup`). Task IDs (UUIDs) are transient — lost on server restart.
- `RepoRegistry` stores entries on disk (temp directory) with a legacy migration path (`_load` converts old format and detects default branch via `_detect_default_branch`). Saving happens synchronously after every mutation.
- Remote branch discovery (`_discover_remote_branches`) uses `git ls-remote` with fnmatch glob patterns; results are cached only during the call — no persistent branch list.
- Default branch detection (`_detect_default_branch`) parses `git symbolic-ref` output; fallback is 'main' if detection fails (handled in `_load` via warning).
- Indexing pipeline functions (`describe_nodes`, `deep_enrich_pages`, `build_batches`, `density_group`) are expected to be synchronous and run inside `run_in_executor` to avoid blocking the event loop.
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
