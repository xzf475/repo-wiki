# indexer/

## Overview

The `indexer` group transforms a codebase into a persistent, searchable knowledge base of symbol definitions, cross-references, and natural language descriptions. It solves the problem of understanding unfamiliar code by automatically generating per-symbol wiki pages and a global index, all cached for incremental updates. The CLI (`cli.py`) orchestrates the workflow: `init` sets up config and git hooks, `run` parses files and writes wiki pages via `indexing.py`, and `serve` exposes a semantic search server (MCP or REST). `embedding.py` generates vector embeddings for symbols and queries, used by the vector store (`vector_store.py`) for similarity search. `indexing.py` is the core: it parses candidates concurrently, caches AST nodes and descriptions, builds cross-references, and renders wiki pages using Jinja templates. The REST API (`rest_api.py`) enables remote search across multiple repositories.

## Modules
| File | Purpose |
|------|---------|
| indexer/rest_api.py | REST API for repo registration, sync, and task management |
| indexer/embedding.py | OpenAI-powered embedding generation for code nodes |
| indexer/cli.py | Command-line interface for indexing and serving wiki |
| indexer/vector_store.py | Chroma vector store for upserting and searching code nodes |
| indexer/indexing.py | Core indexing pipeline with caching and wiki generation |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/cli.py::main` | function | Defines the main Click command group for the CLI. |
| `indexer/cli.py::init` | function | Creates config file, installs pre-commit hook, and appends to CLAUDE.md. |
| `indexer/cli.py::run` | function | Indexes codebase, generates wiki pages for tracked files. |
| `indexer/cli.py::status` | function | Displays last indexed commit, stale files, and manifest statistics. |
| `indexer/cli.py::hook` | function | Defines Click command group for pre-commit hook management. |
| `indexer/cli.py::hook_install` | function | Installs the pre-commit hook script in the current repository. |
| `indexer/cli.py::hook_remove` | function | Removes the pre-commit hook script from the current repository. |
| `indexer/cli.py::serve` | function | Starts the MCP server for semantic code search over the codebase. |
| `indexer/cli.py::serve_api` | function | Starts a REST API server for remote semantic search across multiple repositories. |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures .cache directory is ignored by git by writing .gitignore. |
| `indexer/cli.py::_is_indexable` | function | Checks if a file path matches indexable language patterns. |
| `indexer/embedding.py::_get_openai_client` | function | Creates an OpenAI client instance with configured API key. |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves OpenAI API key from environment variable or .env file. |
| `indexer/embedding.py::_build_text` | function | Builds a text string from ASTNode fields for embedding generation. |
| `indexer/embedding.py::embed_nodes` | function | Computes embeddings for multiple ASTNode objects using threaded API calls. |
| `indexer/embedding.py::embed_query` | function | Computes embedding for a single query string using the API. |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI embedding API with batched texts, implements retry and rate limiting. |
| `indexer/indexing.py::_desc_cache_path` | function | Returns cached descriptions file path, creating parent directory if missing. |
| `indexer/indexing.py::load_cached_descriptions` | function | Loads previously cached symbol descriptions from JSON file. |
| `indexer/indexing.py::save_cached_descriptions` | function | Saves new symbol descriptions to cache, merging with existing entries. |
| `indexer/indexing.py::_file_desc_cache_path` | function | Returns cached file descriptions file path, creating parent directory. |
| `indexer/indexing.py::load_cached_file_descriptions` | function | Loads previously cached file-level descriptions from JSON file. |
| `indexer/indexing.py::save_cached_file_descriptions` | function | Saves new file descriptions to cache, merging with existing entries. |
| `indexer/indexing.py::cross_reference` | function | Builds a cross-reference mapping from caller to callee IDs. |
| `indexer/indexing.py::load_existing_nodes` | function | Loads and merges previously cached ASTNode objects by file hash. |
| `indexer/indexing.py::parse_candidates` | function | Parses multiple candidate files concurrently using thread pool, reusing cache. |
| `indexer/indexing.py::build_batches` | function | Splits a list into batches of given size using len and append. |
| `indexer/indexing.py::write_wiki_pages` | function | Generates wiki pages with context, index entries, and density groups. |
| `indexer/indexing.py::write_index_and_skill` | function | Renders index and skill pages via Jinja templates and current commit. |
| `indexer/indexing.py::update_manifest` | function | Updates manifest with file entries, hashing tracked files and saving. |
| `indexer/indexing.py::_embedding_cache_path` | function | Creates the embedding cache directory if missing. |
| `indexer/indexing.py::_embedding_cache_sig` | function | Computes SHA256 hex digest of built text for cache key. |
| `indexer/indexing.py::load_cached_embeddings` | function | Reads and deserializes cached embeddings from file if exists. |
| `indexer/indexing.py::save_cached_embeddings` | function | Serializes embeddings to JSON and writes to cache with warning. |
| `indexer/indexing.py::upsert_vectors` | function | Upserts or deletes embeddings for tracked files with caching. |
| `indexer/rest_api.py::_get_repo_lock` | function | Returns a Lock instance for per-repo synchronization. |
| `indexer/rest_api.py::TaskStore` | class | Thread-safe store for tracking async tasks with expiry-based cleanup. |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty task store with a thread lock. |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes tasks older than 10 minutes from the store. |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with unique ID and current timestamp. |
| `indexer/rest_api.py::TaskStore.get` | method | Returns task data for given ID, or None if not found. |
| `indexer/rest_api.py::TaskStore.update` | method | Updates an existing task's status and timestamp. |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects remote default branch name using `git ls-remote --symref`. |
| `indexer/rest_api.py::_match_branch_rule` | function | Matches a branch name against comma-separated glob patterns. |
| `indexer/rest_api.py::_discover_remote_branches` | function | Fetches remote branches matching glob patterns via git ls-remote. |
| `indexer/rest_api.py::RepoRegistry` | class | Thread-safe registry for repository configurations with persistent storage. |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Loads existing repo configs from temp directory under lock. |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry data to JSON and writes to temp file. |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from disk, detects default branches, imports configs. |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds or updates a repository configuration, persists after registration. |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes repository, cleans up on-disk state, and evicts client. |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns configuration for a given repo name. |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names. |
| `indexer/rest_api.py::RepoRegistry.items` | method | Returns list of all (name, config) tuples. |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repository metadata fields, raises ValueError for invalid keys. |
| `indexer/rest_api.py::register_repo` | function | Parses request, validates repo, discovers branches, creates register task. |
| `indexer/rest_api.py::task_status` | function | Returns JSON response with task status if exists. |
| `indexer/rest_api.py::validate_repo` | function | Validates repo structure, files, and returns validation results. |
| `indexer/rest_api.py::sync_repo` | function | Creates a sync task to update index incrementally. |
| `indexer/rest_api.py::rebuild_repo` | function | Creates a rebuild task to re-index all branches from scratch. |
| `indexer/rest_api.py::sync_all_branches` | function | Discovers branches, then syncs each branch independently. |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, re-discovers branches, rebuilds all. |
| `indexer/rest_api.py::rebuild_all_branches` | function | Discovers branches, then rebuilds each branch sequentially. |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes deep enrichment, batch processing, and caching for a branch. |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock, runs inner rebuild, updates status. |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Clones repo, configures branches, prunes stale branches, indexes. |
| `indexer/rest_api.py::_run_sync_task` | function | Clones repo, detects changes since last sync, incremental index update. |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock, runs inner register, updates status. |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, discovers branches, indexes each, persists config. |
| `indexer/rest_api.py::unregister_repo` | function | Parses request body and unregisters repository by name. |
| `indexer/rest_api.py::search_symbols` | function | Embeds query, searches vector index, expands results with call graph. |
| `indexer/rest_api.py::trace_call` | function | Parses request, resolves repos, traces call chain implementation. |
| `indexer/rest_api.py::get_source_context` | function | Parses request, reads code lines, returns context with line numbers. |
| `indexer/rest_api.py::list_repos` | function | Returns JSON list of repo names with metadata and webhook URLs. |
| `indexer/rest_api.py::health` | function | Returns JSON status with registered repo count. |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed info about a repository including branches and file counts. |
| `indexer/rest_api.py::update_repo_meta` | function | Parses request body and updates repository metadata. |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates file contents from multiple repositories into one response. |
| `indexer/rest_api.py::_get_webhook_url` | function | Builds webhook URL with HMAC signature from base URL and secret. |
| `indexer/rest_api.py::_webhook_sign` | function | Computes HMAC-SHA256 signature of payload with secret key. |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Compares provided HMAC signature with computed signature using compare_digest. |
| `indexer/rest_api.py::webhook_by_name` | function | Verifies webhook signature, matches branch rules, triggers sync or rebuild. |
| `indexer/rest_api.py::create_app` | function | Builds Starlette app with routes, middleware, and error handlers. |
| `indexer/rest_api.py::_index_page` | function | Returns static HTML index file from template directory. |
| `indexer/rest_api.py::_inject_credentials` | function | Embeds username and token into git URL for authentication. |
| `indexer/rest_api.py::_sanitize_error` | function | Replaces file paths and sensitive patterns in error strings. |
| `indexer/rest_api.py::_store_credentials` | function | Writes token-based credentials to git config file for remote operations. |
| `indexer/rest_api.py::_resolve_repos` | function | Expands repo list to all registered repos if 'default' is specified. |
| `indexer/rest_api.py::_trace_call_impl` | function | Calls retrieval trace function and returns result. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Calls retrieval expansion function and returns result. |
| `indexer/rest_api.py::_InvalidBodyError` | class | Custom exception for invalid request body parsing. |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body, raises _InvalidBodyError on failure. |
| `indexer/rest_api.py::_run_all` | function | Runs sync task under repo lock with status update. |
| `indexer/rest_api.py::_run_all` | function | Runs sync task under repo lock with status update. |
| `indexer/rest_api.py::_run_all` | function | Runs sync task under repo lock with status update. |
| `indexer/rest_api.py::_LoggingMiddleware` | class | Starlette middleware that logs request duration and method. |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request info and execution time, then calls next middleware. |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns 400 JSON response for invalid request body. |
| `indexer/rest_api.py::_AuthMiddleware` | class | Starlette middleware validating bearer token via environment secret. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks Authorization header, returns 401 if token mismatches. |
| `indexer/vector_store.py::_get_client` | function | Returns a PersistentClient for Chroma vector store |
| `indexer/vector_store.py::evict_client` | function | Removes the Chroma client from the global cache |
| `indexer/vector_store.py::_get_or_create_collection` | function | Retrieves or creates a Chroma collection by name |
| `indexer/vector_store.py::upsert_nodes` | function | Inserts or updates nodes in Chroma collection |
| `indexer/vector_store.py::search` | function | Queries Chroma collection for nearest neighbors |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves stored nodes by their IDs from Chroma |
| `indexer/vector_store.py::delete_by_files` | function | Deletes all nodes associated with given file paths |
| `indexer/vector_store.py::_build_doc` | function | Constructs the document text for a node |
| `indexer/vector_store.py::_truncate_list` | function | Truncates a list to fit within metadata size limits |
| `indexer/vector_store.py::_build_meta` | function | Builds metadata dict, truncating long lists |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes object to compact JSON string |
## Data Flows
- User runs `indexer run` → `cli.py::run` resolves tracked files → `parse_candidates` parses each file (with hash-based cache reuse) → `write_wiki_pages` generates per-symbol wiki pages → `write_index_and_skill` writes index/skill pages → `update_manifest` persists file hashes and commit.
- Pre-commit hook triggers `indexer run --staged` → flow similar to above but only processes staged files → updates wiki incrementally → hook exits (fast for small changes).
- User runs `indexer serve` → `create_server` starts MCP server → on query, `embed_query` embeds the query → vector store returns similar symbol nodes → results returned to client.
- User runs `indexer serve-api <repo_dirs>` → `create_app` starts Flask/Werkzeug REST API → POST `/search` with query → embeds query → searches across all provided repos' vector stores → returns ranked symbol results.
## Design Constraints
- Symbol descriptions are cached per-file hash in `<cache_dir>/desc/` and merged on save; incremental runs skip re-generation but new descriptions are added, not overwritten, preserving previous descriptions if API fails.
- Embedding API calls use a uniform random delay (0.5–1.5s) between batches to respect rate limits; `_call_embedding_api` retries on failure but logs a warning and continues with empty embedding on repeated failure.
- `_is_indexable` uses `fnmatch` patterns (e.g., `*.py`, `*.js`) to filter files; it is called on every file in `run` and `status` – non-matching files are silently skipped, not indexed.
- CLI commands (`init`, `run`, `status`, `hook`) all require a valid git repository and call `is_git_repo()` early; they exit with error if not in a git repo.
- `_ensure_cache_gitignore` writes a `.gitignore` into `.cache/` only if one doesn't already contain `*` – it checks each line, so manual edits to that file are preserved.
- Cross-reference mapping (`cross_reference`) uses symbol IDs split by `::` to build caller→callee relationships; symbols without a delimiter (e.g., builtins) are ignored in the graph.
## Relationships
- **Calls:** Choice, Environment, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, OpenAI, PageContext, Path, PersistentClient, RLock, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, _InvalidBodyError, _as_completed, _build_doc, _build_meta, _build_text, _call_embedding_api, _cleanup, _desc_cache_path, _detect_default_branch, _discover_remote_branches, _embedding_cache_path, _embedding_cache_sig, _ensure_cache_gitignore, _expand_retrieval, _expand_with_call_graph, _file_desc_cache_path, _get_client, _get_openai_client, _get_or_create_collection, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_indexable, _match_branch_rule, _parse_body, _resolve_api_key, _resolve_repos, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _store_credentials, _trace_call_impl, _trace_call_retrieval, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, body, bool, build_batches, build_index, build_page, call_next, changed_files_since, chmod, command, compare_digest, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, debug, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, dict, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, fnmatch, fromkeys, get, get_collection, get_or_create_collection, get_running_loop, get_template, gettempdir, glob, group, hasattr, hexdigest, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, len, list, list_names, load_cached_descriptions, load_cached_embeddings, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, option, parse_candidates, parse_file, pop, progress_callback, query, quote, range, read_text, register, relative_to, release, remove_hook, removed_files, removesuffix, render, replace, resolve, result, rewrite_query, rglob, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_descriptions, save_cached_embeddings, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlparse, urlunparse, uuid4, values, vs_delete, vs_upsert, warning, with_suffix, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::changed_files_since, indexer/indexing.py::_embedding_cache_sig, indexer/indexing.py::load_cached_descriptions, indexer/indexing.py::load_cached_embeddings, indexer/indexing.py::load_cached_file_descriptions, indexer/indexing.py::save_cached_descriptions, indexer/indexing.py::save_cached_embeddings, indexer/indexing.py::save_cached_file_descriptions, indexer/indexing.py::upsert_vectors, indexer/llm.py::_describe_files_chunk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::RepoRegistry.unregister, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run
- **Imports from:** __future__.annotations, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding._build_text, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.trace_call, indexer.utils.load_env_file, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, logging, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, urllib.parse, uuid, uvicorn
## Entry Points
- `main`
- `init`
- `status`
- `hook`
- `hook_install`
- `hook_remove`
- `serve`
- `serve_api`
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
- `upsert_nodes`
- `delete_by_files`
