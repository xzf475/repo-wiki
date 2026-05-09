# indexer/

## Overview

The indexer module solves the problem of automatically generating documentation (wiki pages) from a codebase by parsing source files into structured AST nodes, computing embeddings for semantic search, and grouping related code via clustering. It supports multiple languages (Python, JS, Rust, Go, Java, Ruby) through dedicated parsers and a shared `ASTNode` class for symbol representation. The module integrates with git to track file changes and update the index incrementally, and provides both an MCP server and a REST API for semantic code search. Key classes include `Config` (and subconfigs `EmbeddingConfig`, `VectorStoreConfig`) for configuration, `ASTNode` for parsed symbols, and the CLI commands (`init`, `run`, `status`, `hook`, `serve`, `serve_api`) orchestrate the full lifecycle.

## Modules
| File | Purpose |
|------|---------|
| indexer/wiki.py |  |
| indexer/vector_store.py |  |
| indexer/grouper.py |  |
| indexer/ast_parser.py |  |
| indexer/manifest.py |  |
| indexer/retrieval.py |  |
| indexer/ruby_parser.py |  |
| indexer/rest_api.py | REST API for repository registration, indexing, and task management |
| indexer/go_parser.py |  |
| indexer/utils.py |  |
| indexer/config.py |  |
| indexer/java_parser.py |  |
| indexer/indexing.py |  |
| indexer/rust_parser.py |  |
| indexer/js_parser.py |  |
| indexer/mcp_server.py |  |
| indexer/cli.py | CLI for codebase indexing, wiki generation, and MCP server |
| indexer/llm.py |  |
| indexer/git.py |  |
| indexer/embedding.py |  |
| indexer/hooks.py |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class |  |
| `indexer/ast_parser.py::_extract_imports` | function |  |
| `indexer/ast_parser.py::_extract_calls` | function |  |
| `indexer/ast_parser.py::_get_class_method_ids` | function |  |
| `indexer/ast_parser.py::parse_file` | function |  |
| `indexer/ast_parser.py::compute_hash_short` | function |  |
| `indexer/ast_parser.py::load_cached_nodes` | function |  |
| `indexer/ast_parser.py::save_cached_nodes` | function |  |
| `indexer/cli.py::main` | function | Defines CLI command group for the indexer tool |
| `indexer/cli.py::init` | function | Creates config, installs pre-commit hook, appends to CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes codebase and generates wiki pages |
| `indexer/cli.py::status` | function | Shows last indexed commit, stale files, manifest stats |
| `indexer/cli.py::hook` | function | Manages the pre-commit hook command group |
| `indexer/cli.py::hook_install` | function | Installs pre-commit hook in current repo |
| `indexer/cli.py::hook_remove` | function | Removes pre-commit hook from current repo |
| `indexer/cli.py::serve` | function | Starts MCP server for semantic code search |
| `indexer/cli.py::serve_api` | function | Starts REST API server for remote semantic code search |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures cache directory has .gitignore entry |
| `indexer/cli.py::_is_indexable` | function | Checks if a file path matches indexable patterns |
| `indexer/cli.py::_parse_progress` | function | Parses progress data and prints it using echo |
| `indexer/config.py::EmbeddingConfig` | class |  |
| `indexer/config.py::VectorStoreConfig` | class |  |
| `indexer/config.py::Config` | class |  |
| `indexer/config.py::_env` | function |  |
| `indexer/config.py::_apply_env_field` | function |  |
| `indexer/config.py::_env_int` | function |  |
| `indexer/config.py::load_config` | function |  |
| `indexer/config.py::_apply_env` | function |  |
| `indexer/config.py::save_config` | function |  |
| `indexer/embedding.py::_get_openai_client` | function |  |
| `indexer/embedding.py::_resolve_api_key` | function |  |
| `indexer/embedding.py::build_embedding_text` | function |  |
| `indexer/embedding.py::compute_embedding_sig` | function |  |
| `indexer/embedding.py::embed_nodes` | function |  |
| `indexer/embedding.py::embed_query` | function |  |
| `indexer/embedding.py::_call_embedding_api` | function |  |
| `indexer/git.py::_run` | function |  |
| `indexer/git.py::current_commit` | function |  |
| `indexer/git.py::current_branch` | function |  |
| `indexer/git.py::staged_files` | function |  |
| `indexer/git.py::changed_files_since` | function |  |
| `indexer/git.py::all_tracked_files` | function |  |
| `indexer/git.py::is_git_repo` | function |  |
| `indexer/go_parser.py::_get_go_language` | function |  |
| `indexer/go_parser.py::_extract_go_doc` | function |  |
| `indexer/go_parser.py::_extract_imports` | function |  |
| `indexer/go_parser.py::_extract_calls` | function |  |
| `indexer/go_parser.py::_get_receiver` | function |  |
| `indexer/go_parser.py::_get_name` | function |  |
| `indexer/go_parser.py::parse_go_file` | function |  |
| `indexer/go_parser.py::visit` | function |  |
| `indexer/go_parser.py::visit` | function |  |
| `indexer/go_parser.py::visit` | function |  |
| `indexer/grouper.py::density_group` | function |  |
| `indexer/grouper.py::folder_of` | function |  |
| `indexer/grouper.py::prefixes` | function |  |
| `indexer/grouper.py::resolve_group` | function |  |
| `indexer/hooks.py::_hook_command` | function |  |
| `indexer/hooks.py::_hook_script_fresh` | function |  |
| `indexer/hooks.py::_hook_script_append` | function |  |
| `indexer/hooks.py::install_hook` | function |  |
| `indexer/hooks.py::remove_hook` | function |  |
| `indexer/indexing.py::compute_ast_sig` | function | Computes SHA256 hash of AST representation for deduplication |
| `indexer/indexing.py::_atomic_write_json` | function |  |
| `indexer/indexing.py::_desc_cache_dir` | function | Creates cache directory for description files via mkdir |
| `indexer/indexing.py::_desc_shard_key` | function | Generates shard key by lowercasing input string |
| `indexer/indexing.py::load_cached_descriptions` | function |  |
| `indexer/indexing.py::save_cached_descriptions` | function |  |
| `indexer/indexing.py::_file_desc_cache_dir` | function | Creates cache directory for file description files via mkdir |
| `indexer/indexing.py::_fdesc_shard_key` | function | Generates shard key for file descriptions by lowercasing input |
| `indexer/indexing.py::load_cached_file_descriptions` | function |  |
| `indexer/indexing.py::save_cached_file_descriptions` | function |  |
| `indexer/indexing.py::cross_reference` | function |  |
| `indexer/indexing.py::load_existing_nodes` | function |  |
| `indexer/indexing.py::parse_candidates` | function |  |
| `indexer/indexing.py::build_batches` | function |  |
| `indexer/indexing.py::_collect_affected_files` | function | Collects affected files into a set by adding results from get |
| `indexer/indexing.py::write_wiki_pages` | function |  |
| `indexer/indexing.py::write_index_and_skill` | function |  |
| `indexer/indexing.py::update_manifest` | function |  |
| `indexer/indexing.py::_embedding_cache_dir` | function | Creates cache directory for embedding files via mkdir |
| `indexer/indexing.py::_emb_shard_key` | function | Generates shard key for embeddings by lowercasing input |
| `indexer/indexing.py::load_cached_embeddings` | function |  |
| `indexer/indexing.py::save_cached_embeddings` | function |  |
| `indexer/indexing.py::upsert_vectors` | function |  |
| `indexer/indexing.py::_load_one` | function | Loads one cached node, checking prefix and existence, computes short hash |
| `indexer/java_parser.py::_get_java_language` | function |  |
| `indexer/java_parser.py::_extract_javadoc` | function |  |
| `indexer/java_parser.py::_extract_imports` | function |  |
| `indexer/java_parser.py::_extract_calls` | function |  |
| `indexer/java_parser.py::_get_name` | function |  |
| `indexer/java_parser.py::_get_type_name` | function |  |
| `indexer/java_parser.py::parse_java_file` | function |  |
| `indexer/java_parser.py::visit` | function |  |
| `indexer/java_parser.py::visit` | function |  |
| `indexer/java_parser.py::visit` | function |  |
| `indexer/js_parser.py::_get_language` | function |  |
| `indexer/js_parser.py::_extract_jsdoc` | function |  |
| `indexer/js_parser.py::_extract_imports` | function |  |
| `indexer/js_parser.py::_extract_calls` | function |  |
| `indexer/js_parser.py::_get_name` | function |  |
| `indexer/js_parser.py::parse_js_file` | function |  |
| `indexer/js_parser.py::visit` | function |  |
| `indexer/js_parser.py::visit` | function |  |
| `indexer/js_parser.py::visit` | function |  |
| `indexer/llm.py::_EmptyResponseError` | class |  |
| `indexer/llm.py::_is_anthropic` | function |  |
| `indexer/llm.py::_resolve_api_key` | function |  |
| `indexer/llm.py::_litellm_kwargs` | function |  |
| `indexer/llm.py::_litellm_completion` | function |  |
| `indexer/llm.py::_get_anthropic_client` | function |  |
| `indexer/llm.py::_anthropic_completion` | function |  |
| `indexer/llm.py::_should_use_anthropic_sdk` | function |  |
| `indexer/llm.py::_parse_llm_json` | function |  |
| `indexer/llm.py::describe_nodes_batch` | function |  |
| `indexer/llm.py::describe_nodes` | function |  |
| `indexer/llm.py::describe_files` | function |  |
| `indexer/llm.py::_describe_files_chunk` | function |  |
| `indexer/llm.py::deep_enrich_page` | function |  |
| `indexer/llm.py::deep_enrich_pages` | function |  |
| `indexer/llm.py::deep_enrich_index` | function |  |
| `indexer/llm.py::rewrite_query` | function |  |
| `indexer/llm.py::synthesize_commit_message` | function |  |
| `indexer/manifest.py::FileEntry` | class |  |
| `indexer/manifest.py::Manifest` | class |  |
| `indexer/manifest.py::Manifest.stale_files` | method |  |
| `indexer/manifest.py::Manifest.removed_files` | method |  |
| `indexer/manifest.py::compute_hash` | function |  |
| `indexer/manifest.py::load_manifest` | function |  |
| `indexer/manifest.py::save_manifest` | function |  |
| `indexer/manifest.py::_check` | function | Checks manifest entry existence, computes hash, retrieves data |
| `indexer/mcp_server.py::_apply_mcp_auth` | function |  |
| `indexer/mcp_server.py::create_server` | function |  |
| `indexer/mcp_server.py::create_api_server` | function |  |
| `indexer/mcp_server.py::_patched_method` | function |  |
| `indexer/mcp_server.py::search_symbols_tool` | function |  |
| `indexer/mcp_server.py::trace_call_tool` | function |  |
| `indexer/mcp_server.py::get_source_context_tool` | function |  |
| `indexer/mcp_server.py::_api_request` | function |  |
| `indexer/mcp_server.py::_api_get` | function |  |
| `indexer/mcp_server.py::_api_post` | function |  |
| `indexer/mcp_server.py::list_repos` | function |  |
| `indexer/mcp_server.py::search_symbols_tool` | function |  |
| `indexer/mcp_server.py::trace_call_tool` | function |  |
| `indexer/mcp_server.py::get_source_context_tool` | function |  |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class |  |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method |  |
| `indexer/retrieval.py::search_symbols` | function |  |
| `indexer/retrieval.py::trace_call` | function |  |
| `indexer/retrieval.py::get_source_context` | function |  |
| `indexer/retrieval.py::_expand_with_call_graph` | function |  |
| `indexer/retrieval.py::_parse_json_list` | function |  |
| `indexer/ruby_parser.py::_get_ruby_language` | function |  |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function |  |
| `indexer/ruby_parser.py::_extract_imports` | function |  |
| `indexer/ruby_parser.py::_extract_calls` | function |  |
| `indexer/ruby_parser.py::_get_name` | function |  |
| `indexer/ruby_parser.py::parse_ruby_file` | function |  |
| `indexer/ruby_parser.py::visit` | function |  |
| `indexer/ruby_parser.py::visit` | function |  |
| `indexer/ruby_parser.py::visit` | function |  |
| `indexer/rust_parser.py::_get_rust_language` | function |  |
| `indexer/rust_parser.py::_extract_rust_doc` | function |  |
| `indexer/rust_parser.py::_extract_imports` | function |  |
| `indexer/rust_parser.py::_extract_calls` | function |  |
| `indexer/rust_parser.py::_get_name` | function |  |
| `indexer/rust_parser.py::parse_rust_file` | function |  |
| `indexer/rust_parser.py::visit` | function |  |
| `indexer/rust_parser.py::visit` | function |  |
| `indexer/rust_parser.py::visit` | function |  |
| `indexer/utils.py::_rel` | function |  |
| `indexer/utils.py::_node_text` | function |  |
| `indexer/utils.py::load_env_file` | function |  |
| `indexer/vector_store.py::_get_client` | function |  |
| `indexer/vector_store.py::evict_client` | function |  |
| `indexer/vector_store.py::_get_or_create_collection` | function |  |
| `indexer/vector_store.py::upsert_nodes` | function |  |
| `indexer/vector_store.py::search` | function |  |
| `indexer/vector_store.py::get_by_ids` | function |  |
| `indexer/vector_store.py::delete_by_files` | function |  |
| `indexer/vector_store.py::_build_doc` | function |  |
| `indexer/vector_store.py::_truncate_list` | function |  |
| `indexer/vector_store.py::_build_meta` | function |  |
| `indexer/vector_store.py::json_dumps_compact` | function |  |
| `indexer/wiki.py::PageContext` | class |  |
| `indexer/wiki.py::IndexEntry` | class |  |
| `indexer/wiki.py::_jinja_env` | function |  |
| `indexer/wiki.py::build_page` | function |  |
| `indexer/wiki.py::build_index` | function |  |
| `indexer/wiki.py::sanitize_group_label` | function |  |
| `indexer/wiki.py::write_page` | function |  |
| `indexer/wiki.py::write_index` | function |  |
| `indexer/rest_api.py::_get_repo_lock` | function | Returns a threading Lock for a repository |
| `indexer/rest_api.py::TaskStore` | class | Manages async task lifecycle with timeout cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes task store with a lock |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks by checking timestamps and sorting |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with unique ID, runs cleanup after |
| `indexer/rest_api.py::TaskStore.get` | method | Retrieves task dict by its ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task properties like status and timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Uses git ls-remote to detect the remote's default branch |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks branch name against glob patterns from a comma-separated rule |
| `indexer/rest_api.py::_discover_remote_branches` | function | Finds remote branches matching glob patterns via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repositories with persistence |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry with a thread lock and temporary directory |
| `indexer/rest_api.py::RepoRegistry._save` | method | Serializes registry to JSON and writes to a temporary file atomically |
| `indexer/rest_api.py::RepoRegistry._load` | method | Reads registry JSON from disk and loads it, detecting default branches |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers a new repo configuration and persists registry |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes repo from registry, evicts client, and saves state |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repo info dict by name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names |
| `indexer/rest_api.py::RepoRegistry.items` | method | Returns list of registered repo entries |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repo metadata like branch or index path |
| `indexer/rest_api.py::register_repo` | function | Async endpoint to register a new repo by URL, clone, and index |
| `indexer/rest_api.py::task_status` | function | Returns JSON status of a task by walking task store |
| `indexer/rest_api.py::validate_repo` | function | Validates a registered repo's manifest and index consistency |
| `indexer/rest_api.py::sync_repo` | function | Triggers a sync task to update repo from remote branch |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers a rebuild task to re-index all branches for a repo |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all remote branches for a registered repo via background tasks |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates repo metadata, discovers branches, and rebuilds index |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds all branches for a repo, re-indexing each branch |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs the full indexing pipeline: hash, cross-reference, enrich, write |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and runs the inner rebuild task |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Executes the actual rebuild: clones, installs hooks, indexes, cleans up |
| `indexer/rest_api.py::_run_sync_task` | function | Syncs repo: fetches, checks indexability, calls indexing pipeline |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and runs the register inner task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, discovers branches, injects credentials, indexes all |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repo by name and returns confirmation |
| `indexer/rest_api.py::search_symbols` | function | Searches symbol names across repos with query rewriting and embedding |
| `indexer/rest_api.py::trace_call` | function | Traces a function call across repos and returns call chain |
| `indexer/rest_api.py::get_source_context` | function | Returns source code lines for a symbol in a specific file |
| `indexer/rest_api.py::list_repos` | function | Lists all registered repos with metadata like webhook URL |
| `indexer/rest_api.py::health` | function | Returns JSON health status with registered repo count |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed info for a repo: branches, manifests, indexes |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repo metadata fields like skip patterns or index config |
| `indexer/rest_api.py::multi_repo_skill` | function | Generates a multi-repo skill file aggregating all repo content |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs the webhook URL for a repo with signature |
| `indexer/rest_api.py::_webhook_sign` | function | Creates HMAC-SHA256 signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook signature against payload using HMAC |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook for a repo, triggering sync or rebuild |
| `indexer/rest_api.py::create_app` | function | Builds and returns the Starlette application with routes and middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the static index.html file or returns 404 |
| `indexer/rest_api.py::_inject_credentials` | function | Injects username/password into a repository URL |
| `indexer/rest_api.py::_sanitize_error` | function | Redacts sensitive paths from error messages |
| `indexer/rest_api.py::_store_credentials` | function | Stores or updates credentials in a netrc file for git access |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names from request body or all registered |
| `indexer/rest_api.py::_trace_call_impl` | function | Executes the trace call retrieval via _trace_call_retrieval |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results with call graph via _expand_retrieval |
| `indexer/rest_api.py::_InvalidBodyError` | class | Custom exception for invalid request body parsing |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body and raises error if invalid |
| `indexer/rest_api.py::_run_all` | function | Runs a specific indexing task under a repo lock |
| `indexer/rest_api.py::_run_all` | function | Runs a specific indexing task under a repo lock |
| `indexer/rest_api.py::_run_all` | function | Runs a specific indexing task under a repo lock |
| `indexer/rest_api.py::_LoggingMiddleware` | class | Starlette middleware that logs request duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request processing time and delegates to next handler |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns 400 JSON response for invalid body |
| `indexer/rest_api.py::_AuthMiddleware` | class | Starlette middleware that validates API key header |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates Authorization header token using HMAC comparison |
## Data Flows
- CLI `run` → iterates git-tracked files → `parse_file` dispatches to language-specific parser → extracts imports, calls, class methods → `compute_hash_short` for cache invalidation → `indexing.py` generates vector embeddings → stores in vector store → generates wiki pages via `wiki.py`
- MCP server query → receives search request → retrieves nearest neighbors from vector store → returns ranked symbol results with context from wiki/grouper
- CLI `init` → creates config file → installs pre-commit hook (via `hooks.py`) → appends entry to `CLAUDE.md` for tool awareness
- Pre-commit hook → computes diff of staged files → re-parses only changed files via caching → updates vector store and wiki incrementally
## Design Constraints
- Only files tracked by git are indexed; untracked or ignored files are skipped (enforced by `_is_indexable` + git ls-files).
- Caching uses SHA256 hash of raw file bytes; cache is invalidated only when content changes, not on metadata changes like timestamps.
- Each language parser is a separate module (e.g., `js_parser.py`, `rust_parser.py`); adding a new language requires implementing `parse_<lang>_file` and registering in `parse_file` dispatch.
- The `grouper.py` uses density-based clustering (likely HDBSCAN) on embeddings to group symbols; this is non-deterministic and may produce different groupings on re-runs if the seed is not fixed.
- The vector store is ephemeral by default (in-memory or local file) unless configured for a cloud backend; `load_existing_nodes` only restores cached AST nodes, not embeddings.
- The pre-commit hook runs on `git commit` but does not block the commit if indexing fails; the `run` command must be invoked manually to rebuild the entire index if the hook is not used.
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, Environment, FastMCP, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Parser, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _as_completed, _atomic_write_json, _build_doc, _build_meta, _call_embedding_api, _cleanup, _collect_affected_files, _compute_file_hash, _desc_cache_dir, _desc_shard_key, _detect_default_branch, _discover_remote_branches, _emb_shard_key, _embedding_cache_dir, _ensure_cache_gitignore, _env, _env_int, _expand_retrieval, _expand_with_call_graph, _extract_calls, _extract_go_doc, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _extract_rust_doc, _fdesc_shard_key, _file_desc_cache_dir, _get_anthropic_client, _get_class_method_ids, _get_client, _get_go_language, _get_java_language, _get_language, _get_name, _get_openai_client, _get_or_create_collection, _get_receiver, _get_repo_lock, _get_ruby_language, _get_rust_language, _get_webhook_url, _hook_command, _hook_script_append, _hook_script_fresh, _inject_credentials, _is_anthropic, _is_indexable, _jinja_env, _litellm_completion, _litellm_kwargs, _load_one, _match_branch_rule, _node_text, _orig_method, _parse_body, _parse_json_list, _parse_llm_json, _rel, _resolve_api_key, _resolve_repos, _run, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _trace_call_retrieval, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, asdict, body, bool, build_batches, build_embedding_text, build_index, build_page, call_next, changed_files_since, child_by_field_name, chmod, command, compare_digest, completion, compute_ast_sig, compute_embedding_sig, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, debug, decode, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, fnmatch, folder_of, fromkeys, get, get_by_ids, get_collection, get_docstring, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, glob, group, hasattr, hexdigest, id, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_names, load, load_cached_descriptions, load_cached_embeddings, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, pop, prefixes, progress_callback, query, quote, range, read, read_bytes, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_group, result, rewrite_query, rfind, rglob, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_descriptions, save_cached_embeddings, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, tool, trace_call, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, with_suffix, write, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::compute_embedding_sig, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/indexing.py::_load_one, indexer/indexing.py::load_cached_descriptions, indexer/indexing.py::load_cached_embeddings, indexer/indexing.py::load_cached_file_descriptions, indexer/indexing.py::load_existing_nodes, indexer/indexing.py::parse_candidates, indexer/indexing.py::save_cached_descriptions, indexer/indexing.py::save_cached_embeddings, indexer/indexing.py::save_cached_file_descriptions, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/indexing.py::write_wiki_pages, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_anthropic_completion, indexer/llm.py::_describe_files_chunk, indexer/llm.py::_litellm_completion, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::_check, indexer/manifest.py::load_manifest, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::RepoRegistry.register, indexer/rest_api.py::RepoRegistry.unregister, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::write_page, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default, tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic, tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty, tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing._collect_affected_files, indexer.indexing.build_batches, indexer.indexing.compute_ast_sig, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_go, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_rust, tree_sitter_typescript, typing.Optional, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
## Entry Points
- `main`
- `init`
- `status`
- `hook`
- `hook_install`
- `hook_remove`
- `serve`
- `serve_api`
- `describe_nodes_batch`
- `describe_nodes`
- `describe_files`
- `deep_enrich_page`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `upsert_nodes`
- `delete_by_files`
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
