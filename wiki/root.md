# ./

## Overview

This module implements the REST API layer for a repository indexing service. It exposes endpoints to register, sync, rebuild, and validate code repositories, converting their files into vector embeddings via an asynchronous indexing pipeline. Key classes include `TaskStore`, which manages in-memory background tasks with expiration-based cleanup, and `RepoRegistry`, which persists repository metadata (e.g., URL, branches, last indexed time) to a JSON file in a temp directory. The module bridges HTTP requests (via FastAPI route handlers) to domain operations like branch discovery (`_discover_remote_branches`), git operations, and vector upsertion (`_run_indexing_pipeline`), coordinating them with per-repo locks to prevent concurrent writes.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository indexing task management and registration |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a Lock object for repository synchronization |
| `indexer/rest_api.py::TaskStore` | class | Stores and manages indexing tasks with cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes the TaskStore instance |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks from the store |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with a unique ID and timestamp |
| `indexer/rest_api.py::TaskStore.get` | method | Returns the task data for a given ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task data and refreshes its last access time |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects the default branch name using git ls-remote |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks if branch name matches a glob pattern rule |
| `indexer/rest_api.py::_discover_remote_branches` | function | Finds remote branches matching glob patterns via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registration and metadata of indexed repositories |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates the temporary directory for registry files |
| `indexer/rest_api.py::RepoRegistry._save` | method | Writes the registry state to a JSON file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from file, detecting default branches |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds a repository to the registry with its config |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository from the registry |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository metadata for a given name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates metadata of a registered repository |
| `indexer/rest_api.py::register_repo` | function | Registers a new repository, discovers branches, and starts indexing |
| `indexer/rest_api.py::task_status` | function | Returns the JSON status of a given task ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repository index against its manifest and files |
| `indexer/rest_api.py::sync_repo` | function | Triggers a sync task for a repository's current state |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers a full rebuild of a repository's index |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all discovered branches of a repository |
| `indexer/rest_api.py::reindex_repo` | function | Updates repo meta, re-discovers branches, and rebuilds index |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds the index for all branches of a repository |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes the full indexing pipeline from files to vectors |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repository lock and runs the rebuild task |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Performs index rebuild: clone repo, run indexing, save |
| `indexer/rest_api.py::_run_sync_task` | function | Incrementally syncs repository index from current state |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock and runs the registration task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Performs repository registration: clone, index, store credentials |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository from the registry |
| `indexer/rest_api.py::search_symbols` | function | Searches symbols across repositories with query expansion |
| `indexer/rest_api.py::trace_call` | function | Traces the call graph of a symbol across repositories |
| `indexer/rest_api.py::get_source_context` | function | Returns source code lines for a given file and line range |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repositories with metadata and webhook |
| `indexer/rest_api.py::health` | function | Returns a JSON health status with count of repos |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repository information including file tree |
| `indexer/rest_api.py::update_repo_meta` | function | Updates metadata fields for a registered repository |
| `indexer/rest_api.py::multi_repo_skill` | function | Returns aggregated file contents and metadata from multiple repos |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs the webhook URL for a repository |
| `indexer/rest_api.py::_webhook_sign` | function | Creates an HMAC-SHA256 signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook payload signature using constant-time compare |
| `indexer/rest_api.py::webhook_by_name` | function | Processes incoming GitHub webhook events for a repo |
| `indexer/rest_api.py::create_app` | function | Builds and configures the Starlette application with routes and middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the frontend HTML index page or API response |
| `indexer/rest_api.py::_inject_credentials` | function | Injects credentials into a repository URL for authentication |
| `indexer/rest_api.py::_sanitize_error` | function | Removes sensitive information from error messages |
| `indexer/rest_api.py::_store_credentials` | function | Stores repository credentials in a git-credential file |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repository names to their configurations |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements recursion-aware call graph traversal |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands a set of symbols with all transitive callees |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON-formatted list of strings |
| `indexer/rest_api.py::_parse_body` | function | Parses a Starlette request body as a dictionary |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all repositories |
| `indexer/rest_api.py::_rebuild_all` | function |  |
| `indexer/rest_api.py::_run_all` | function | Runs sync task for all repositories |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request method, path, and duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request details and timing to info logger |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that validates JWT tokens from Authorization header |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates bearer token and rejects unauthorized requests |
## Data Flows
- POST /register → `register_repo()` creates a task, discovers remote branches via `_discover_remote_branches()`, and schedules `run_in_executor` to start indexing
- GET /task/{id} → `task_status()` returns the JSON status from `TaskStore.get()`
- POST /reindex → `reindex_repo()` updates RepoRegistry metadata, re‑discovers branches, then creates and schedules a rebuild task
- POST /sync-all-branches → `sync_all_branches()` discovers branches, creates a task per branch, and runs `_run_sync_task` for each via executor
## Design Constraints
- Repo names must be unique; `register_repo()` checks `RepoRegistry.get()` — if a repo with that name already exists, it returns an error (implied by `_run_rebuild_task_inner` calling `register` on a dict that may already exist).
- Task IDs are UUID4 strings; tasks expire silently after a timeout (`_cleanup` sorted by timestamp, but no explicit TTL in symbols — the cleanup logic uses `time.time() - created` > some threshold).
- Per-repo locking via `_get_repo_lock` (a `Lock` object) ensures only one rebuild/sync task runs per repository at a time; `acquire`/`release` are explicit in `_run_rebuild_task`.
- Branch discovery uses `git ls-remote` and glob matching (`fnmatch`) against configured `branch_rules`; if no branches match, the operation is a no‑op (len check).
- Validation (`validate_repo`) compares the local index against `load_manifest` and `all_tracked_files`, computing a sum of stale files; an empty index filesystem path is not considered stale.
- The registry is saved atomically to a JSON file (in system tempdir) after every mutation (`_save` writes `json.dumps` → `write_text`); loading falls back to detecting default branch via `_detect_default_branch` if registry doesn't exist.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, Route, Starlette, StaticFiles, ValueError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _match_branch_rule, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, any, append, body, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_git_repo, is_relative_to, isinstance, items, iter, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, match, max, min, mkdir, mount, new, next, now, parse_candidates, quote, range, read_text, register, relative_to, release, removed_files, removeprefix, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_rebuild_all, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call
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
