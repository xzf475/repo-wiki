# ./

## Overview

['This module implements the REST API layer for the indexer service, exposing endpoints to register, validate, sync, and rebuild repositories. It solves the coordination problem of managing long-running indexing tasks asynchronously while maintaining persistent state (repo preferences via RepoRegistry) and in-memory task progress (TaskStore). Key classes are TaskStore (thread-safe, auto-expiring task metadata) and RepoRegistry (RLock-protected, atomically persisted JSON store of repo configs). Functions like register_repo, sync_repo, and reindex_repo enqueue background indexing work via the event loop executor, ensuring per-repo mutual exclusion via threading.Lock acquired from _get_repo_lock.']

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repository registration and indexing management |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/rest_api.py::_get_repo_lock` | function | Acquires a threading Lock for a repo by name. |
| `indexer/rest_api.py::TaskStore` | class | In-memory store tracking async task state with auto-cleanup. |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty dict of tasks under a lock. |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks older than expiry threshold from store. |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with UUID and timestamp, runs cleanup. |
| `indexer/rest_api.py::TaskStore.get` | method | Returns task dict by ID, or None if missing. |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task fields and refreshes timestamp. |
| `indexer/rest_api.py::_detect_default_branch` | function | Runs git ls-remote to detect default branch of remote. |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks branch name against comma-separated glob patterns. |
| `indexer/rest_api.py::_discover_remote_branches` | function | Lists remote branches matching glob patterns via git ls-remote. |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repositories with persistent JSON storage. |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates data dir and initializes an RLock for concurrency. |
| `indexer/rest_api.py::RepoRegistry._save` | method | Writes registry dict to a JSON file atomically. |
| `indexer/rest_api.py::RepoRegistry._load` | method | Reads and validates registry JSON, detects default branches. |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds repo with config, saves, and logs info. |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes repo by name, saves, and logs info. |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repo config dict by name or None. |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names. |
| `indexer/rest_api.py::RepoRegistry.items` | method | Returns list of (name, config) pairs from registry. |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repo metadata fields and persists changes. |
| `indexer/rest_api.py::register_repo` | function | Validates URL, clones, registers, and enqueues indexing async. |
| `indexer/rest_api.py::task_status` | function | Returns status dict for a specific async task. |
| `indexer/rest_api.py::validate_repo` | function | Checks repo structure, indexability, and counts stale files. |
| `indexer/rest_api.py::sync_repo` | function | Enqueues a sync indexing task for all branches async. |
| `indexer/rest_api.py::rebuild_repo` | function | Enqueues a full rebuild indexing task async. |
| `indexer/rest_api.py::sync_all_branches` | function | Acquires repo lock, discovers branches, enqueues sync per branch. |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, rediscovers branches, enqueues full rebuild. |
| `indexer/rest_api.py::rebuild_all_branches` | function | Acquires repo lock, discovers branches, enqueues rebuild per branch. |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs full indexing: parse, enrich, upsert vectors, write results. |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and runs inner rebuild task. |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Clones repo, runs indexing pipeline, installs hooks, cleans up. |
| `indexer/rest_api.py::_run_sync_task` | function | Fetches changes, runs incremental indexing, handles stale files. |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and runs inner register task. |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, injects credentials, runs indexing, installs hooks. |
| `indexer/rest_api.py::unregister_repo` | function | Parses body and unregisters repo from registry. |
| `indexer/rest_api.py::search_symbols` | function | Queries vector store, expands call graph, returns sorted results. |
| `indexer/rest_api.py::trace_call` | function | Traces call chain from symbol up to depth limit async. |
| `indexer/rest_api.py::get_source_context` | function | Reads source lines around a given line number from files. |
| `indexer/rest_api.py::list_repos` | function | Returns list of registered repos with metadata and webhook URLs. |
| `indexer/rest_api.py::health` | function | Returns simple health status based on registry size. |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed branch info, file stats, and commit data. |
| `indexer/rest_api.py::update_repo_meta` | function | Parses body and updates repo meta fields in registry. |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates skill files from multiple repos with path filtering. |
| `indexer/rest_api.py::_get_webhook_url` | function | Builds webhook URL for a repo using host config and secret sign. |
| `indexer/rest_api.py::_webhook_sign` | function | Creates HMAC-SHA256 signature of repo name with secret. |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies request signature against expected HMAC-SHA256. |
| `indexer/rest_api.py::webhook_by_name` | function | Verifies signature, matches branch rule, enqueues sync or rebuild. |
| `indexer/rest_api.py::create_app` | function | Builds and configures Starlette app with routes, middleware, static files. |
| `indexer/rest_api.py::_index_page` | function | Serves frontend index.html with injected repo list JSON. |
| `indexer/rest_api.py::_inject_credentials` | function | Embeds username/password into a Git remote URL. |
| `indexer/rest_api.py::_sanitize_error` | function | Strips sensitive paths from error message strings. |
| `indexer/rest_api.py::_store_credentials` | function | Writes credential helper script to repo .git with chmod. |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names or IDs to list of config dicts. |
| `indexer/rest_api.py::_trace_call_impl` | function | Recursively resolves call chains up to depth limit. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands symbol list with transitive callees for search. |
| `indexer/rest_api.py::_parse_json_list` | function | Parses a JSON string into a list, returns empty on failure. |
| `indexer/rest_api.py::_InvalidBodyError` | class | Exception class for invalid request body content. |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body, raises _InvalidBodyError on failure. |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs rebuild task for all branches. |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs rebuild task for all branches. |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs rebuild task for all branches. |
| `indexer/rest_api.py::_LoggingMiddleware` | class | Logs request method, path, and duration via Starlette middleware. |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Records start time, calls next, logs elapsed time. |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns 400 JSON response for invalid body errors. |
| `indexer/rest_api.py::_AuthMiddleware` | class | Validates API key token in Authorization header. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks token against configured API key, returns 403 if mismatch. |
## Data Flows
- client calls register_repo -> validates URL, git clones, adds to RepoRegistry, enqueues async indexing via loop.run_in_executor (creates task in TaskStore returned as task_id)
- client calls sync_repo -> fetches repo config from RepoRegistry, discovers remote branches via _discover_remote_branches (git ls-remote + glob matching), enqueues _run_sync_task per branch under repo lock
- client calls reindex_repo -> acquires repo lock, calls RepoRegistry.update_meta (persists updated config), redisovers branches, enqueues _run_rebuild_task_inner per branch, updates task status atomic
- background _run_indexing_pipeline runs parse_candidates, describe_files, upsert_vectors, and write_index_and_skill in sequence, updating TaskStore on progress/completion
## Design Constraints
- Concurrency per repo is strictly serialized: _get_repo_lock returns a threading.Lock local to the module, not shared across processes, so only one indexing task per repo can run inside a single worker.
- TaskStore._cleanup runs on every create() call (not on a timer), removing tasks older than a fixed expiry threshold; thus stale tasks are only purged coincident with new task creation.
- RepoRegistry persists as JSON to a temp directory (via gettempdir) under a subfolder '.indexify/registry'; the file is written atomically by writing to a temp suffix and then replacing the original.
- Branch pattern matching in _match_branch_rule uses Python's fnmatch on comma-separated globs, but each pattern is stripped; no support for negated patterns or regex.
- Default branch detection (_detect_default_branch) uses `git ls-remote --symref <url> HEAD` and parses the first line; relies on git being installed and network access at registration time.
- register_repo blocks the web thread for clone (via run_in_executor); synchronous file operations may cause timeouts if git clone is slow, but there is no explicit timeout exposed.
## Relationships
- **Calls:** HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, Path, RLock, Route, Starlette, StaticFiles, ValueError, _InvalidBodyError, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _expand_with_call_graph, _get_client, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _match_branch_rule, _parse_body, _parse_json_list, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, all_tracked_files, any, append, body, bool, build_batches, build_index, call_next, changed_files_since, chmod, compare_digest, count, create, cross_reference, current_commit, deep_enrich_index, deep_enrich_pages, defaultdict, density_group, describe_files, describe_nodes, dumps, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, get, get_by_ids, get_collection, get_running_loop, gettempdir, glob, hasattr, hexdigest, info, install_hook, int, is_dir, is_git_repo, is_relative_to, isinstance, items, iter, iterdir, join, json, keys, len, list, list_names, load_config, load_existing_nodes, load_manifest, loads, locked, lower, match, max, min, mkdir, mount, new, next, now, parse_candidates, pop, quote, range, read_text, register, relative_to, release, removed_files, removesuffix, replace, resolve, rewrite_query, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_config, save_manifest, search, set, setdefault, sort, sorted, split, splitlines, stale_files, startswith, str, strftime, strip, sub, sum, time, unlink, unregister, update, update_manifest, update_meta, upsert_vectors, urlparse, urlunparse, uuid4, values, warning, with_suffix, write_index, write_index_and_skill, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::serve_api, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::run
- **Imports from:** __future__.annotations, asyncio, collections.defaultdict, datetime.datetime, datetime.timezone, fnmatch, hashlib, hmac, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.utils.load_env_file, indexer.vector_store._get_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.wiki.IndexEntry, indexer.wiki.build_index, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, json, logging, os, pathlib.Path, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.parse, uuid
## Entry Points
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
