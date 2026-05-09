# indexer/

## Overview

The indexer module solves the problem of making a large, multi-language codebase semantically searchable for LLMs and developers. It parses source files into structured ASTNode objects (symbols with names, types, docstrings, call graphs) using language-specific parsers (Java, JS, Ruby, etc.), computes embeddings via OpenAI API, stores vectors in a local vector store, and exposes search through CLI commands (`run`, `serve`), an MCP server for IDE integration, and a REST API for multi-repo search. Key classes include `ASTNode` (symbol representation), `Config` (manages embedding, store, and index settings), and `EmbeddingConfig` / `VectorStoreConfig` as sub-configs. The module is the core of a documentation-augmented code assistant that keeps a manifest of indexed files and supports incremental updates via git hooks.

## Modules
| File | Purpose |
|------|---------|
| indexer/java_parser.py | Java source code parser using tree-sitter |
| indexer/ast_parser.py | AST-based code parser with import and call extraction |
| indexer/llm.py | LLM integration for describing code symbols |
| indexer/cli.py | Command-line interface for indexing and serving wiki |
| indexer/rest_api.py | REST API for repo registration, sync, and task management |
| indexer/manifest.py | Manifest file handling for indexed repositories |
| indexer/go_parser.py | Go source code parser for symbol extraction |
| indexer/embedding.py | OpenAI-powered embedding generation for code nodes |
| indexer/vector_store.py | Chroma vector store for upserting and searching code nodes |
| indexer/hooks.py | Management of pre-commit hooks for repo indexing |
| indexer/indexing.py | Core indexing pipeline with caching and wiki generation |
| indexer/rust_parser.py | Tree-sitter parser for Rust source files |
| indexer/retrieval.py | Symbol search, call graph tracing, and source context retrieval |
| indexer/mcp_server.py | MCP server exposing code search and trace tools |
| indexer/js_parser.py | JavaScript source code parser using tree-sitter |
| indexer/utils.py | Utility functions for file paths and environment loading |
| indexer/config.py | Configuration management for embedding and vector store |
| indexer/grouper.py | File and symbol grouping utilities for indexing |
| indexer/ruby_parser.py | Tree-sitter parser for Ruby source files |
| indexer/wiki.py | Generates static wiki pages and index from indexed code |
| indexer/git.py | Git repository utilities for tracking changes |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class | Represents a code symbol with id, name, type, docstring, line range, and calls. |
| `indexer/ast_parser.py::_extract_imports` | function | Walks AST to extract imported module names and aliases. |
| `indexer/ast_parser.py::_extract_calls` | function | Walks AST to extract names of functions called within a node. |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Walks AST to collect IDs of methods defined in a class node. |
| `indexer/ast_parser.py::parse_file` | function | Parses a source file into ASTNodes by dispatching to language-specific parsers. |
| `indexer/ast_parser.py::compute_hash_short` | function | Computes SHA256 hex digest of file bytes, returns first 8 characters. |
| `indexer/ast_parser.py::load_cached_nodes` | function | Loads previously cached ASTNode objects from a JSON cache file. |
| `indexer/ast_parser.py::save_cached_nodes` | function | Serializes ASTNode objects to JSON and writes to cache file. |
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
| `indexer/config.py::EmbeddingConfig` | class | Configuration dataclass for embedding model API settings. |
| `indexer/config.py::VectorStoreConfig` | class | Configuration dataclass for vector store settings. |
| `indexer/config.py::Config` | class | Top-level configuration dataclass combining embedding, store, and index settings. |
| `indexer/config.py::_env` | function | Reads environment variable value with optional default. |
| `indexer/config.py::_apply_env_field` | function | Sets config field from environment variable if present. |
| `indexer/config.py::_env_int` | function | Reads environment variable as integer, returns default on error. |
| `indexer/config.py::load_config` | function | Loads configuration from .indexer.toml file, applies environment overrides. |
| `indexer/config.py::_apply_env` | function | Applies all environment variable overrides to the configuration object. |
| `indexer/config.py::save_config` | function | Saves configuration object to .indexer.toml using atomic write. |
| `indexer/embedding.py::_get_openai_client` | function | Creates an OpenAI client instance with configured API key. |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves OpenAI API key from environment variable or .env file. |
| `indexer/embedding.py::build_embedding_text` | function | Joins and appends text to build embedding text |
| `indexer/embedding.py::compute_embedding_sig` | function | Computes SHA256 hex digest of embedding text |
| `indexer/embedding.py::embed_nodes` | function | Computes embeddings for multiple ASTNode objects using threaded API calls. |
| `indexer/embedding.py::embed_query` | function | Computes embedding for a single query string using the API. |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI embedding API with batched texts, implements retry and rate limiting. |
| `indexer/git.py::_run` | function | Runs a git command, captures stdout, warns on errors. |
| `indexer/git.py::current_commit` | function | Returns the current git commit hash. |
| `indexer/git.py::current_branch` | function | Returns the current git branch name. |
| `indexer/git.py::staged_files` | function | Returns list of files staged for commit. |
| `indexer/git.py::changed_files_since` | function | Returns list of files changed since a given commit hash. |
| `indexer/git.py::all_tracked_files` | function | Returns list of all git-tracked files in the repository. |
| `indexer/git.py::is_git_repo` | function | Returns True if current working directory is a git repository. |
| `indexer/go_parser.py::_get_go_language` | function | Returns tree-sitter Language object for Golang. |
| `indexer/go_parser.py::_extract_go_doc` | function | Extracts doc comment text from a Go function or type node. |
| `indexer/go_parser.py::_extract_imports` | function | Extracts import paths from Go source using tree-sitter. |
| `indexer/go_parser.py::_extract_calls` | function | Extracts names of function calls from a Go AST node. |
| `indexer/go_parser.py::_get_receiver` | function | Returns the receiver type name for a Go method declaration. |
| `indexer/go_parser.py::_get_name` | function | Returns the name string from a Go function or type node. |
| `indexer/go_parser.py::parse_go_file` | function | Parses a Go source file into ASTNode objects using tree-sitter. |
| `indexer/go_parser.py::visit` | function | Recursive visitor that extracts ASTNodes from Go file. |
| `indexer/go_parser.py::visit` | function | Recursive visitor that extracts ASTNodes from Go file. |
| `indexer/go_parser.py::visit` | function | Recursive visitor that extracts ASTNodes from Go file. |
| `indexer/grouper.py::density_group` | function | Groups file paths into density-based clusters using subdirectory prefixes. |
| `indexer/grouper.py::folder_of` | function | Returns the parent directory path of a given file path. |
| `indexer/grouper.py::prefixes` | function | Generates all prefix directory paths from root to file location. |
| `indexer/grouper.py::resolve_group` | function | Resolves the optimal density-based group for a given file path. |
| `indexer/hooks.py::_hook_command` | function | Returns the Click command string for the repo-wiki hook. |
| `indexer/hooks.py::_hook_script_fresh` | function | Generates the full hook script content for a fresh install. |
| `indexer/hooks.py::_hook_script_append` | function | Generates the appended block for existing non-repo-wiki hooks. |
| `indexer/hooks.py::install_hook` | function | Installs or updates the pre-commit hook script, handling fresh and append cases. |
| `indexer/hooks.py::remove_hook` | function | Removes the repo-wiki-managed portion from the pre-commit hook file. |
| `indexer/indexing.py::_desc_cache_path` | function | Returns cached descriptions file path, creating parent directory if missing. |
| `indexer/indexing.py::_atomic_write_json` | function | Writes JSON to file atomically using temporary file and replace |
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
| `indexer/indexing.py::load_cached_embeddings` | function | Reads and deserializes cached embeddings from file if exists. |
| `indexer/indexing.py::save_cached_embeddings` | function | Serializes embeddings to JSON and writes to cache with warning. |
| `indexer/indexing.py::upsert_vectors` | function | Upserts or deletes embeddings for tracked files with caching. |
| `indexer/java_parser.py::_get_java_language` | function | Returns tree-sitter Language object for Java. |
| `indexer/java_parser.py::_extract_javadoc` | function | Extracts and cleans Javadoc comment text from tree-sitter node. |
| `indexer/java_parser.py::_extract_imports` | function | Visits AST to collect import statements as list of strings. |
| `indexer/java_parser.py::_extract_calls` | function | Visits AST to collect function call names as a set. |
| `indexer/java_parser.py::_get_name` | function | Extracts identifier name from tree-sitter node via field. |
| `indexer/java_parser.py::_get_type_name` | function | Extracts type name identifier from tree-sitter node via field. |
| `indexer/java_parser.py::parse_java_file` | function | Parses Java file with tree-sitter, extracting symbols and metadata. |
| `indexer/java_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/java_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/java_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/js_parser.py::_get_language` | function | Returns tree-sitter Language for JS/TS/TSX based on extension. |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts and cleans JSDoc comment text from tree-sitter node. |
| `indexer/js_parser.py::_extract_imports` | function | Visits AST to collect import statements as list of strings. |
| `indexer/js_parser.py::_extract_calls` | function | Visits AST to collect function call names as a set. |
| `indexer/js_parser.py::_get_name` | function | Extracts identifier name from tree-sitter node via field. |
| `indexer/js_parser.py::parse_js_file` | function | Parses JS/TS file with tree-sitter, extracting symbols and metadata. |
| `indexer/js_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/js_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/js_parser.py::visit` | function | Recursive AST visitor for extracting imports, calls, and definitions. |
| `indexer/llm.py::_EmptyResponseError` | class | Custom exception for empty LLM response. |
| `indexer/llm.py::_is_anthropic` | function | Checks if model identifier indicates Anthropic API model. |
| `indexer/llm.py::_resolve_api_key` | function | Resolves API key from environment variable or config with fallback. |
| `indexer/llm.py::_litellm_kwargs` | function | Returns keyword arguments for LiteLLM API call. |
| `indexer/llm.py::_litellm_completion` | function | Calls LiteLLM completion with retry and empty response handling. |
| `indexer/llm.py::_get_anthropic_client` | function | Initializes and returns Anthropic client instance. |
| `indexer/llm.py::_anthropic_completion` | function | Calls Anthropic completion with retry and error handling. |
| `indexer/llm.py::_should_use_anthropic_sdk` | function | Determines if Anthropic SDK should be used based on model. |
| `indexer/llm.py::_parse_llm_json` | function | Parses LLM JSON response with recovery for truncation and errors. |
| `indexer/llm.py::describe_nodes_batch` | function | Sends batch of code nodes to LLM for description, returns parsed JSON. |
| `indexer/llm.py::describe_nodes` | function | Describes code nodes using thread pool and batched LLM calls. |
| `indexer/llm.py::describe_files` | function | Describes code files using thread pool and batched LLM calls. |
| `indexer/llm.py::_describe_files_chunk` | function | Sends chunk of file descriptions to LLM and returns parsed JSON. |
| `indexer/llm.py::deep_enrich_page` | function | Uses LLM to deep-enrich a wiki page with additional context. |
| `indexer/llm.py::deep_enrich_pages` | function | Deep-enriches multiple wiki pages in parallel via thread pool. |
| `indexer/llm.py::deep_enrich_index` | function | Uses LLM to deep-enrich the index page with structured data. |
| `indexer/llm.py::rewrite_query` | function | Rewrites search queries using LLM to improve retrieval recall. |
| `indexer/llm.py::synthesize_commit_message` | function | Generates commit message from diff using LLM with cleanup. |
| `indexer/manifest.py::FileEntry` | class | Data class for file entry with hash and metadata. |
| `indexer/manifest.py::Manifest` | class | Container for FileEntry mappings and stale/removed detection. |
| `indexer/manifest.py::Manifest.stale_files` | method | Returns files with changed hashes or missing as stale entries. |
| `indexer/manifest.py::Manifest.removed_files` | method | Returns files present in manifest but missing on disk. |
| `indexer/manifest.py::compute_hash` | function | Computes SHA256 hex digest of file contents with error warning. |
| `indexer/manifest.py::load_manifest` | function | Loads and deserializes Manifest from JSON file, handles missing. |
| `indexer/manifest.py::save_manifest` | function | Writes Manifest to JSON file atomically using temporary file. |
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Applies HTTP Basic Auth or token auth to MCP API requests. |
| `indexer/mcp_server.py::create_server` | function | Creates FastMCP server with search, trace, and source tools. |
| `indexer/mcp_server.py::create_api_server` | function | Creates FastMCP API server with remote repo access and HTTP endpoints. |
| `indexer/mcp_server.py::_patched_method` | function | Monkey-patched authentication method for MCP middleware. |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols by natural language query with call graph expansion. |
| `indexer/mcp_server.py::trace_call_tool` | function | Sends trace call request to API, returns formatted call chain. |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code around lines, returns code with line numbers and padding. |
| `indexer/mcp_server.py::_api_request` | function | Sends HTTP request to remote API with JSON payload and parses response. |
| `indexer/mcp_server.py::_api_get` | function | Sends HTTP GET request via _api_request. |
| `indexer/mcp_server.py::_api_post` | function | Sends HTTP POST request via _api_request. |
| `indexer/mcp_server.py::list_repos` | function | Lists registered repositories with descriptions, tags, and stats. |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches symbols by natural language query with call graph expansion. |
| `indexer/mcp_server.py::trace_call_tool` | function | Sends trace call request to API, returns formatted call chain. |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code around lines, returns code with line numbers and padding. |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | FastAPI middleware validating MCP access token against environment secret. |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Validates bearer token using constant-time comparison, returns 401 if invalid. |
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
| `indexer/retrieval.py::search_symbols` | function | Embeds query, searches index, expands results via call graph. |
| `indexer/retrieval.py::trace_call` | function | Retrieves symbol and recurses through called functions to build chain. |
| `indexer/retrieval.py::get_source_context` | function | Reads file lines with range validation, returns code with numbers. |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Adds called/caller symbols to result set up to depth limit. |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON string into list, returns empty list on failure. |
| `indexer/ruby_parser.py::_get_ruby_language` | function | Loads and returns tree-sitter Ruby language singleton. |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function | Parses comment blocks preceding a node, returns cleaned docstring. |
| `indexer/ruby_parser.py::_extract_imports` | function | Traverses AST to collect all require/require_relative statements. |
| `indexer/ruby_parser.py::_extract_calls` | function | Traverses AST to collect all method call identifiers. |
| `indexer/ruby_parser.py::_get_name` | function | Extracts the identifier text from a method or class definition node. |
| `indexer/ruby_parser.py::parse_ruby_file` | function | Parses Ruby source with tree-sitter, extracts symbols with metadata. |
| `indexer/ruby_parser.py::visit` | function | Recursively traverses AST to collect import statements. |
| `indexer/ruby_parser.py::visit` | function | Recursively traverses AST to collect import statements. |
| `indexer/ruby_parser.py::visit` | function | Recursively traverses AST to collect import statements. |
| `indexer/rust_parser.py::_get_rust_language` | function | Creates a tree-sitter Language object for Rust |
| `indexer/rust_parser.py::_extract_rust_doc` | function | Extracts and cleans Rust doc comments from node text |
| `indexer/rust_parser.py::_extract_imports` | function | Traverses AST to collect import statement texts |
| `indexer/rust_parser.py::_extract_calls` | function | Traverses AST to collect function call names |
| `indexer/rust_parser.py::_get_name` | function | Extracts symbol name from a named AST node |
| `indexer/rust_parser.py::parse_rust_file` | function | Parses a Rust file into ASTNode list with imports, calls, docs |
| `indexer/rust_parser.py::visit` | function | Recursively visits AST nodes, extracting docstrings and calls |
| `indexer/rust_parser.py::visit` | function | Recursively visits AST nodes, extracting docstrings and calls |
| `indexer/rust_parser.py::visit` | function | Recursively visits AST nodes, extracting docstrings and calls |
| `indexer/utils.py::_rel` | function | Computes relative path from a directory to a file |
| `indexer/utils.py::_node_text` | function | Decodes a tree-sitter node's byte span to a string |
| `indexer/utils.py::load_env_file` | function | Reads and parses a .env file into an environment dict |
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
| `indexer/wiki.py::PageContext` | class | Holds page rendering context with group and symbols |
| `indexer/wiki.py::IndexEntry` | class | Represents a single index entry with label and href |
| `indexer/wiki.py::_jinja_env` | function | Creates a Jinja2 Environment with file system loader |
| `indexer/wiki.py::build_page` | function | Renders a wiki page from template given symbols and group |
| `indexer/wiki.py::build_index` | function | Renders an index page using Jinja template |
| `indexer/wiki.py::sanitize_group_label` | function | Cleans a group label by replacing underscores and filtering |
| `indexer/wiki.py::write_page` | function | Writes a wiki page HTML file to disk |
| `indexer/wiki.py::write_index` | function | Writes the index HTML file to disk |
| `indexer/ast_parser.py::ASTNode` | class | Represents a code symbol with id, name, type, docstring, line range, and calls. |
| `indexer/ast_parser.py::_extract_imports` | function | Walks AST to extract imported module names and aliases. |
| `indexer/ast_parser.py::_extract_calls` | function | Walks AST to extract names of functions called within a node. |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Walks AST to collect IDs of methods defined in a class node. |
| `indexer/ast_parser.py::parse_file` | function | Parses a source file into ASTNodes by dispatching to language-specific parsers. |
| `indexer/ast_parser.py::compute_hash_short` | function | Computes SHA256 hex digest of file bytes, returns first 8 characters. |
| `indexer/ast_parser.py::load_cached_nodes` | function | Loads previously cached ASTNode objects from a JSON cache file. |
| `indexer/ast_parser.py::save_cached_nodes` | function | Serializes ASTNode objects to JSON and writes to cache file. |
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
| `indexer/cli.py::_parse_progress` | function | Parses progress data and prints it using echo |
| `indexer/embedding.py::_get_openai_client` | function | Creates an OpenAI client instance with configured API key. |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves OpenAI API key from environment variable or .env file. |
| `indexer/embedding.py::build_embedding_text` | function | Joins and appends text to build embedding text |
| `indexer/embedding.py::compute_embedding_sig` | function | Computes SHA256 hex digest of embedding text |
| `indexer/embedding.py::embed_nodes` | function | Computes embeddings for multiple ASTNode objects using threaded API calls. |
| `indexer/embedding.py::embed_query` | function | Computes embedding for a single query string using the API. |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI embedding API with batched texts, implements retry and rate limiting. |
| `indexer/manifest.py::FileEntry` | class | Data class for file entry with hash and metadata. |
| `indexer/manifest.py::Manifest` | class | Container for FileEntry mappings and stale/removed detection. |
| `indexer/manifest.py::Manifest.stale_files` | method | Returns files with changed hashes or missing as stale entries. |
| `indexer/manifest.py::Manifest.removed_files` | method | Returns files present in manifest but missing on disk. |
| `indexer/manifest.py::compute_hash` | function | Computes SHA256 hex digest of file contents with error warning. |
| `indexer/manifest.py::load_manifest` | function | Loads and deserializes Manifest from JSON file, handles missing. |
| `indexer/manifest.py::save_manifest` | function | Writes Manifest to JSON file atomically using temporary file. |
| `indexer/manifest.py::_check` | function | Checks manifest entry existence, computes hash, retrieves data |
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
| `indexer/indexing.py::compute_ast_sig` | function | Computes SHA256 hash of AST representation for deduplication |
| `indexer/indexing.py::_atomic_write_json` | function | Writes JSON to file atomically using temporary file and replace |
| `indexer/indexing.py::_desc_cache_dir` | function | Creates cache directory for description files via mkdir |
| `indexer/indexing.py::_desc_shard_key` | function | Generates shard key by lowercasing input string |
| `indexer/indexing.py::load_cached_descriptions` | function | Loads previously cached symbol descriptions from JSON file. |
| `indexer/indexing.py::save_cached_descriptions` | function | Saves new symbol descriptions to cache, merging with existing entries. |
| `indexer/indexing.py::_file_desc_cache_dir` | function | Creates cache directory for file description files via mkdir |
| `indexer/indexing.py::_fdesc_shard_key` | function | Generates shard key for file descriptions by lowercasing input |
| `indexer/indexing.py::load_cached_file_descriptions` | function | Loads previously cached file-level descriptions from JSON file. |
| `indexer/indexing.py::save_cached_file_descriptions` | function | Saves new file descriptions to cache, merging with existing entries. |
| `indexer/indexing.py::cross_reference` | function | Builds a cross-reference mapping from caller to callee IDs. |
| `indexer/indexing.py::load_existing_nodes` | function | Loads and merges previously cached ASTNode objects by file hash. |
| `indexer/indexing.py::parse_candidates` | function | Parses multiple candidate files concurrently using thread pool, reusing cache. |
| `indexer/indexing.py::build_batches` | function | Splits a list into batches of given size using len and append. |
| `indexer/indexing.py::_collect_affected_files` | function | Collects affected files into a set by adding results from get |
| `indexer/indexing.py::write_wiki_pages` | function | Generates wiki pages with context, index entries, and density groups. |
| `indexer/indexing.py::write_index_and_skill` | function | Renders index and skill pages via Jinja templates and current commit. |
| `indexer/indexing.py::update_manifest` | function | Updates manifest with file entries, hashing tracked files and saving. |
| `indexer/indexing.py::_embedding_cache_dir` | function | Creates cache directory for embedding files via mkdir |
| `indexer/indexing.py::_emb_shard_key` | function | Generates shard key for embeddings by lowercasing input |
| `indexer/indexing.py::load_cached_embeddings` | function | Reads and deserializes cached embeddings from file if exists. |
| `indexer/indexing.py::save_cached_embeddings` | function | Serializes embeddings to JSON and writes to cache with warning. |
| `indexer/indexing.py::upsert_vectors` | function | Upserts or deletes embeddings for tracked files with caching. |
| `indexer/indexing.py::_load_one` | function | Loads one cached node, checking prefix and existence, computes short hash |
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
## Data Flows
- CLI `run` command → `parse_file` dispatches to language parsers → extracts ASTNodes → computes SHA256 hash for caching → enriches pages via `deep_enrich_pages` → updates manifest and writes wiki files.
- Pre-commit hook → `_ensure_cache_gitignore` ensures cache is git-ignored → re-indexes changed files (stale files) → updates manifest and wiki.
- MCP server or REST API query → `retrieval` module uses vector store to find relevant ASTNodes → returns semantic search results (symbols and their context).
- Config loading: reads `.indexer.toml` → applies environment variable overrides (e.g., `OPENAI_API_KEY`, model name, dimensions) → returns `Config` object used by embedding and vector store.
## Design Constraints
- AST parsing results are cached on disk using SHA256 hashes of file bytes; cache invalidated only when file content changes (not on timestamp).
- Config file is written atomically using `NamedTemporaryFile` + `replace` to avoid partial writes.
- The `_is_indexable` function uses **fnmatch** patterns; files outside tracked language extensions are silently skipped during indexing.
- Embedding API key resolution falls back to `.env` file parsing; if neither environment variable nor `.env` contains `OPENAI_API_KEY`, the client creation will fail at runtime.
- The `parse_file` dispatcher only handles `.java`, `.js`, `.rb`, `.py`, `.go`, `.rs`; other file types are ignored (no generic fallback).
- Vector store is ephemeral per repository; the REST API serves multiple repos by aggregating separate vector stores in a directory (`repos_path`).
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, Environment, FastMCP, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Parser, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _as_completed, _atomic_write_json, _build_doc, _build_meta, _call_embedding_api, _cleanup, _collect_affected_files, _compute_file_hash, _desc_cache_dir, _desc_cache_path, _desc_shard_key, _detect_default_branch, _discover_remote_branches, _emb_shard_key, _embedding_cache_dir, _embedding_cache_path, _ensure_cache_gitignore, _env, _env_int, _expand_retrieval, _expand_with_call_graph, _extract_calls, _extract_go_doc, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _extract_rust_doc, _fdesc_shard_key, _file_desc_cache_dir, _file_desc_cache_path, _get_anthropic_client, _get_class_method_ids, _get_client, _get_go_language, _get_java_language, _get_language, _get_name, _get_openai_client, _get_or_create_collection, _get_receiver, _get_repo_lock, _get_ruby_language, _get_rust_language, _get_webhook_url, _hook_command, _hook_script_append, _hook_script_fresh, _inject_credentials, _is_anthropic, _is_indexable, _jinja_env, _litellm_completion, _litellm_kwargs, _load_one, _match_branch_rule, _node_text, _orig_method, _parse_body, _parse_json_list, _parse_llm_json, _rel, _resolve_api_key, _resolve_repos, _run, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _trace_call_retrieval, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, asdict, body, bool, build_batches, build_embedding_text, build_index, build_page, call_next, changed_files_since, child_by_field_name, chmod, command, compare_digest, completion, compute_ast_sig, compute_embedding_sig, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, debug, decode, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, fnmatch, folder_of, fromkeys, get, get_by_ids, get_collection, get_docstring, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, glob, group, hasattr, hexdigest, id, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_names, load, load_cached_descriptions, load_cached_embeddings, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_file, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, pop, prefixes, progress_callback, query, quote, range, read, read_bytes, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_group, result, rewrite_query, rfind, rglob, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_descriptions, save_cached_embeddings, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, tool, trace_call, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, with_suffix, write, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
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
- `main`
- `init`
- `status`
- `hook`
- `hook_install`
- `hook_remove`
- `serve`
- `serve_api`
- `upsert_nodes`
- `delete_by_files`
- `compute_ast_sig`
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
