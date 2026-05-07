# indexer/

## Overview

The indexer module implements a semantic code indexing pipeline that converts codebases into vector embeddings for LLM-powered search and retrieval. It solves the problem of enabling natural language queries over code by extracting symbols, generating embeddings via OpenAI, and storing them for similarity search. The module is structured around a `Config` dataclass (embedding parameters, vector store settings), CLI commands (`run`, `serve`, `init`, `status`) that orchestrate indexing lifecycle, and backend services (MCP server, REST API) that expose indexed data to external tools like Claude. This fits the broader architecture as the semantic memory layer: code is indexed offline and queried online to provide context-aware code answers.

## Modules
| File | Purpose |
|------|---------|
| indexer/mcp_server.py | MCP server exposing code search and trace tools |
| indexer/indexing.py | Caches and writes indexed descriptions and wiki pages |
| indexer/cli.py | CLI entry point for indexing, hooks, and server commands |
| indexer/utils.py | Utility functions for indexing text nodes and environment |
| indexer/vector_store.py | Vector store operations for upserting and searching embeddings |
| indexer/rest_api.py | REST API for repository registration and indexing management |
| indexer/embedding.py | OpenAI-based embedding for nodes and queries |
| indexer/git.py | Git repository inspection and file tracking utilities |
| indexer/llm.py | Generates descriptions using LLM API calls |
| indexer/config.py | Configuration loading and saving for embedding and vector store |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/cli.py::main` | function | Entry point that groups CLI subcommands under a common command group |
| `indexer/cli.py::init` | function | Creates config file, installs pre-commit hook, updates CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes codebase by loading config, tracking files, generating wiki pages |
| `indexer/cli.py::status` | function | Displays last commit, stale files, and manifest statistics |
| `indexer/cli.py::hook` | function | Groups subcommands for pre-commit hook management |
| `indexer/cli.py::hook_install` | function | Installs pre-commit hook using config and repo path |
| `indexer/cli.py::hook_remove` | function | Removes pre-commit hook from the repository |
| `indexer/cli.py::serve` | function | Starts MCP server for semantic code search and wiki access |
| `indexer/cli.py::serve_api` | function | Starts REST API for multi-repo semantic code search |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures .indexer cache directory is added to .gitignore |
| `indexer/cli.py::_is_indexable` | function | Checks if a file path is indexable using fnmatch patterns |
| `indexer/config.py::EmbeddingConfig` | class | Dataclass for embedding model configuration fields |
| `indexer/config.py::VectorStoreConfig` | class | Dataclass for vector storage configuration fields |
| `indexer/config.py::Config` | class | Main configuration dataclass combining all sub-configs |
| `indexer/config.py::_env` | function | Reads environment variable value with optional default |
| `indexer/config.py::_apply_env_field` | function | Sets configuration field from environment variable if present |
| `indexer/config.py::_env_int` | function | Reads integer environment variable, logs warning on failure |
| `indexer/config.py::load_config` | function | Loads configuration from TOML file with environment variable overrides |
| `indexer/config.py::_apply_env` | function | Applies environment variable overrides to all configuration fields |
| `indexer/config.py::save_config` | function | Saves configuration to TOML file atomically using temporary file |
| `indexer/embedding.py::_get_openai_client` | function | Creates configured OpenAI client instance for embeddings |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves API key from environment variable with file support |
| `indexer/embedding.py::_build_text` | function | Builds embedding text by joining node signature and docstring |
| `indexer/embedding.py::embed_nodes` | function | Embeds multiple code nodes using concurrent OpenAI API calls |
| `indexer/embedding.py::embed_query` | function | Embeds a query string using the embedding API |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI embedding API with rate limit handling and retries |
| `indexer/git.py::_run` | function | Runs a git command and returns stripped stdout |
| `indexer/git.py::current_commit` | function | Returns current git commit hash |
| `indexer/git.py::current_branch` | function | Returns current git branch name |
| `indexer/git.py::staged_files` | function | Lists files staged in git index |
| `indexer/git.py::changed_files_since` | function | Returns files changed since a given commit hash |
| `indexer/git.py::all_tracked_files` | function | Lists all files tracked by git in working tree |
| `indexer/git.py::is_git_repo` | function | Checks if current directory is a git repository |
| `indexer/indexing.py::_desc_cache_path` | function | Returns path to the node descriptions cache file |
| `indexer/indexing.py::load_cached_descriptions` | function | Loads cached node descriptions from JSON file |
| `indexer/indexing.py::save_cached_descriptions` | function | Saves node descriptions to cache file, merging with existing |
| `indexer/indexing.py::_file_desc_cache_path` | function | Returns path to file descriptions cache file |
| `indexer/indexing.py::load_cached_file_descriptions` | function | Loads cached file descriptions from JSON file |
| `indexer/indexing.py::save_cached_file_descriptions` | function | Saves file descriptions to cache file, merging with existing |
| `indexer/indexing.py::cross_reference` | function | Builds cross-reference mapping from function calls to callers |
| `indexer/indexing.py::load_existing_nodes` | function | Loads existing parsed nodes from cache and current files |
| `indexer/indexing.py::parse_candidates` | function | Parses candidate files into nodes using cached and new results |
| `indexer/indexing.py::build_batches` | function | Groups nodes into batches for LLM processing |
| `indexer/indexing.py::write_wiki_pages` | function | Generates and writes wiki pages from indexed nodes |
| `indexer/indexing.py::write_index_and_skill` | function | Writes index page and skill configuration files |
| `indexer/indexing.py::update_manifest` | function | Updates manifest with current commit and file entries |
| `indexer/indexing.py::upsert_vectors` | function | Upserts node embeddings into vector store for changed files |
| `indexer/llm.py::_EmptyResponseError` | class | Custom exception for empty LLM responses |
| `indexer/llm.py::_is_anthropic` | function | Checks if model ID is from Anthropic provider |
| `indexer/llm.py::_resolve_api_key` | function | Resolves LLM provider API key from environment variable |
| `indexer/llm.py::_litellm_kwargs` | function | Builds LiteLLM completion kwargs with default parameters |
| `indexer/llm.py::_litellm_completion` | function | Calls LiteLLM completion with exponential backoff retries |
| `indexer/llm.py::_get_anthropic_client` | function | Creates configured Anthropic client instance |
| `indexer/llm.py::_anthropic_completion` | function | Calls Anthropic API completion with rate limit handling and retries |
| `indexer/llm.py::_should_use_anthropic_sdk` | function | Determines whether to use Anthropic SDK based on model |
| `indexer/llm.py::_parse_llm_json` | function | Parses LLM JSON response with recovery for truncation and malformed output |
| `indexer/llm.py::describe_nodes_batch` | function | Describes multiple code nodes using LLM in a single batch call |
| `indexer/llm.py::describe_nodes` | function | Describes multiple code nodes concurrently using batched LLM calls |
| `indexer/llm.py::describe_files` | function | Generates descriptions for multiple files using concurrent LLM calls |
| `indexer/llm.py::_describe_files_chunk` | function | Describes a chunk of files using LLM in a single batch call |
| `indexer/llm.py::deep_enrich_page` | function | Deeply enriches a single wiki page with additional LLM-generated content |
| `indexer/llm.py::deep_enrich_pages` | function | Deeply enriches multiple wiki pages concurrently using LLM |
| `indexer/llm.py::deep_enrich_index` | function | Enriches index with deep LLM analysis using litellm or anthropic completion |
| `indexer/llm.py::rewrite_query` | function | Rewrites search query using LLM for better recall |
| `indexer/llm.py::synthesize_commit_message` | function | Synthesizes commit message from diff using LLM |
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Applies MCP authentication middleware with HMAC digest comparison |
| `indexer/mcp_server.py::create_server` | function | Creates MCP server with tools for local indexer interactions |
| `indexer/mcp_server.py::create_api_server` | function | Creates MCP server proxying to remote API via HTTP requests |
| `indexer/mcp_server.py::_patched_method` | function | Patched method applying MCP auth middleware |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols across one or all repos with optional query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph for a symbol across repos via API |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source context from a file in a specific repo |
| `indexer/mcp_server.py::_api_request` | function | Makes raw HTTP API request with JSON encoding/decoding |
| `indexer/mcp_server.py::_api_get` | function | Performs GET request via _api_request |
| `indexer/mcp_server.py::_api_post` | function | Performs POST request via _api_request |
| `indexer/mcp_server.py::list_repos` | function | Lists registered repositories with names, descriptions, and stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols across one or all repos with optional query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph for a symbol across repos via API |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source context from a file in a specific repo |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware for MCP authentication via HMAC token |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Dispatches request after verifying Authorization header HMAC |
| `indexer/rest_api.py::_get_repo_lock` | function | Returns a threading Lock for a given repo name |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for tracking async task statuses |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes TaskStore with an empty dict and lock |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks beyond retention timeout |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task entry with unique ID and timestamp |
| `indexer/rest_api.py::TaskStore.get` | method | Gets task status dict by task ID or returns None |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task status dict and refreshes timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects default branch name using git symbolic-ref or ls-remote |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks if branch name matches a comma-separated glob pattern |
| `indexer/rest_api.py::_discover_remote_branches` | function | Fetches remote branches matching glob patterns via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Thread-safe registry for repository metadata and state |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes RepoRegistry with temporary storage and RLock |
| `indexer/rest_api.py::RepoRegistry._save` | method | Saves registry dict to JSON file with atomic replace |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON file, detecting default branches |
| `indexer/rest_api.py::RepoRegistry.register` | method | Registers or updates a repository with its config |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Unregisters a repository and evicts its client resources |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository configuration dict by name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names |
| `indexer/rest_api.py::RepoRegistry.items` | method | Returns list of (repo_name, config_dict) pairs |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repository metadata fields like description and tags |
| `indexer/rest_api.py::register_repo` | function | Registers a new repository from a git URL, cloning and indexing |
| `indexer/rest_api.py::task_status` | function | Returns JSON with task status or 404 if not found |
| `indexer/rest_api.py::validate_repo` | function | Validates repository health, returns index summary and issues |
| `indexer/rest_api.py::sync_repo` | function | Triggers asynchronous incremental sync of a repository |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers asynchronous full rebuild of a repository |
| `indexer/rest_api.py::sync_all_branches` | function | Syncs all remote branches matching glob patterns for a repo |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates repo meta, rediscovers branches, and rebuilds |
| `indexer/rest_api.py::rebuild_all_branches` | function | Rebuilds index for each remote branch matching glob patterns |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Runs full indexing pipeline: file description, enrichment, vector upsert |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and executes inner rebuild task |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Executes full rebuild: clone, index, enrich, and write vectors |
| `indexer/rest_api.py::_run_sync_task` | function | Performs incremental sync: fetch changes, index new/modified files |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and executes inner registration task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repository, discovers branches, and initializes index |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters a repository by name via JSON request |
| `indexer/rest_api.py::search_symbols` | function | Searches code symbols with query, expands call graph, returns results |
| `indexer/rest_api.py::trace_call` | function | Traces call graph for a symbol up to configurable depth |
| `indexer/rest_api.py::get_source_context` | function | Returns source code context lines for a file range |
| `indexer/rest_api.py::list_repos` | function | Lists registered repositories with description, tags, and stats |
| `indexer/rest_api.py::health` | function | Returns health status with number of registered repos |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repository info including branches, stats, and manifests |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repository metadata like description and tags |
| `indexer/rest_api.py::multi_repo_skill` | function | Builds context for multi-repo skill by aggregating files from multiple repos |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook callback URL with timestamp and HMAC signature |
| `indexer/rest_api.py::_webhook_sign` | function | Computes HMAC-SHA256 signature for webhook payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Verifies webhook request HMAC signature using constant-time comparison |
| `indexer/rest_api.py::webhook_by_name` | function | Processes incoming webhook event for a repository by name |
| `indexer/rest_api.py::create_app` | function | Creates and configures the Starlette ASGI application with routes and middleware |
| `indexer/rest_api.py::_index_page` | function | Serves the main index HTML page or returns 404 if missing |
| `indexer/rest_api.py::_inject_credentials` | function | Injects credentials into URL by parsing and rebuilding with quoting |
| `indexer/rest_api.py::_sanitize_error` | function | Sanitizes error messages by replacing patterns via sub and replace |
| `indexer/rest_api.py::_store_credentials` | function | Stores credentials to file, sets permissions, and quotes URL components |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repository list from dictionary items via get |
| `indexer/rest_api.py::_trace_call_impl` | function | Implements trace call by delegating to _trace_call_retrieval |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands retrieval using call graph via _expand_retrieval |
| `indexer/rest_api.py::_InvalidBodyError` | class | Custom exception class for invalid request body |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body, raises _InvalidBodyError on invalid input |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock, runs sync or rebuild task, updates metadata |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock, runs sync or rebuild task, updates metadata |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock, runs sync or rebuild task, updates metadata |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request dispatch times |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request time and calls next middleware |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns JSON 400 response for invalid request body |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware for API key authentication via Bearer token |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates Bearer token constant-time comparison, returns 401 on mismatch |
| `indexer/utils.py::_rel` | function | Computes relative path from given path to current directory |
| `indexer/utils.py::_node_text` | function | Decodes node text using default encoding |
| `indexer/utils.py::load_env_file` | function | Loads .env file, strips quotes, returns dictionary of environment variables |
| `indexer/vector_store.py::_get_client` | function | Creates and returns a PersistentClient instance |
| `indexer/vector_store.py::evict_client` | function | Evicts the client from cache using pop |
| `indexer/vector_store.py::_get_or_create_collection` | function | Gets or creates a Chroma collection, returns it |
| `indexer/vector_store.py::upsert_nodes` | function | Upserts nodes into vector store, updating and deleting as needed |
| `indexer/vector_store.py::search` | function | Searches vector store with query, returns results with distances |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves nodes by IDs from vector store |
| `indexer/vector_store.py::delete_by_files` | function | Deletes nodes from vector store by file paths |
| `indexer/vector_store.py::_build_doc` | function | Builds document string from node text and metadata |
| `indexer/vector_store.py::_truncate_list` | function | Truncates list to maximum allowed size with warning |
| `indexer/vector_store.py::_build_meta` | function | Builds metadata dictionary, truncating long values |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes JSON with compact separators |
## Data Flows
- CLI `run` → `load_config` → `all_tracked_files` → `embed_nodes` (per file symbol) → `save_cached_nodes` → vector store write
- CLI `serve` → `create_server` (MCP) → receives query → `embed_query` → vector store search → returns ranked code snippets
- CLI `init` → `save_config` → `install_hook` (git pre-commit) → updates CLAUDE.md with index metadata
- CLI `status` → `load_manifest` → compare tracked vs committed files → reports stale index entries and last commit
## Design Constraints
- API key resolution supports file-based secrets: if env var ends with '_FILE', its value is treated as a file path whose contents are read as the key.
- Embedding text is built only from node `signature` and `docstring` (not full source body) to avoid exceeding token limits of the embedding model.
- Configuration is loaded from a TOML file but each field can be overridden by environment variables (using `_env`, `_env_int` helpers) with no warning if the file is missing; defaults are set via dataclass field defaults.
- Vector store configuration has a `store_dir` that defaults relative to the repo root; the actual store driver is abstracted (e.g., dummy for testing, proper vector DB in production).
- Git operations assume `cwd` is a git repo; failures produce warnings and empty results, not exceptions, to allow graceful degradation in non-git directories.
## Relationships
- **Calls:** Anthropic, Choice, Config, EmbeddingConfig, Environment, FastMCP, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _build_doc, _build_meta, _build_text, _call_embedding_api, _cleanup, _desc_cache_path, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _env, _env_int, _expand_retrieval, _expand_with_call_graph, _file_desc_cache_path, _get_anthropic_client, _get_client, _get_openai_client, _get_or_create_collection, _get_repo_lock, _get_webhook_url, _inject_credentials, _is_anthropic, _is_indexable, _litellm_completion, _litellm_kwargs, _match_branch_rule, _orig_method, _parse_body, _parse_llm_json, _resolve_api_key, _resolve_repos, _run, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _trace_call_retrieval, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, body, bool, build_batches, build_index, build_page, call_next, changed_files_since, chmod, command, compare_digest, completion, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, debug, decode, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, describe_files, describe_nodes, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, fnmatch, fromkeys, get, get_collection, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, glob, group, hasattr, hexdigest, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, len, list, list_names, load, load_cached_descriptions, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse_candidates, parse_file, pop, progress_callback, query, quote, range, read, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, result, rewrite_query, rfind, rglob, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_descriptions, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, tool, trace_call, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, vs_delete, vs_upsert, warning, with_suffix, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/ast_parser.py::parse_file, indexer/cli.py::hook_install, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/indexing.py::load_cached_descriptions, indexer/indexing.py::load_cached_file_descriptions, indexer/indexing.py::save_cached_descriptions, indexer/indexing.py::save_cached_file_descriptions, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_anthropic_completion, indexer/llm.py::_describe_files_chunk, indexer/llm.py::_litellm_completion, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::RepoRegistry.register, indexer/rest_api.py::RepoRegistry.unregister, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default, tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run
- **Imports from:** __future__.annotations, anthropic, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.utils.load_env_file, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, typing.Optional, urllib.error, urllib.parse, urllib.request, uuid, uvicorn
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
- `deep_enrich_page`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
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
