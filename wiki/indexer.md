# indexer/

## Overview

The indexer module transforms a source code repository into a semantic wiki of code symbols (ASTNode) by parsing files into structured metadata (name, type, docstring, calls, etc.), computing embeddings, and caching results to disk. It solves the problem of codebase navigation by enabling large language models (via MCP or REST API) to retrieve relevant symbol context for a given query. Key classes: ASTNode (dataclass for symbol metadata), Config (with EmbeddingConfig/VectorStoreConfig for settings), and language-specific parsers (java_parser, ruby_parser, etc.) selected by file extension. The module integrates with git via pre-commit hooks to re-index only changed files and maintains a manifest to track indexing state.

## Modules
| File | Purpose |
|------|---------|
| indexer/cli.py | CLI for indexing, server, and hook management |
| indexer/java_parser.py | Parses Java source into structured node representations |
| indexer/ruby_parser.py | Parses Ruby source into structured node representations |
| indexer/git.py | Git utilities for file tracking and commits |
| indexer/rust_parser.py | Parses Rust source into structured node representations |
| indexer/indexing.py | Core indexing pipeline from parse to wiki pages |
| indexer/ast_parser.py | Python AST parser with node extraction and caching |
| indexer/vector_store.py | ChromaDB vector store for embedding persistence |
| indexer/go_parser.py | Parses Go source into structured node representations |
| indexer/js_parser.py | Parses JavaScript/TypeScript source into structured nodes |
| indexer/grouper.py | Groups files into wiki pages by density |
| indexer/config.py | Configuration with env overrides and defaults |
| indexer/hooks.py | Installs and manages pre-commit indexing hooks |
| indexer/retrieval.py | Semantic search and call graph tracing engine |
| indexer/embedding.py | Generates embeddings for code nodes and queries |
| indexer/wiki.py | Generates wiki pages from indexed symbols |
| indexer/rest_api.py | REST API for multi-repo indexing management |
| indexer/utils.py | Utilities for relative paths and environment loading |
| indexer/manifest.py | Manages file hash manifest for incremental indexing |
| indexer/llm.py | LLM integration for symbol and file descriptions |
| indexer/mcp_server.py | MCP server for semantic code search tools |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class | Dataclass representing a parsed code symbol with metadata |
| `indexer/ast_parser.py::_extract_imports` | function | Extracts import names from an AST tree via walk |
| `indexer/ast_parser.py::_extract_calls` | function | Collects function call names within an AST node |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Returns set of method IDs defined in a class node |
| `indexer/ast_parser.py::parse_file` | function | Parses source file into ASTNodes using language-specific parsers |
| `indexer/ast_parser.py::compute_hash_short` | function | Computes SHA256 hex digest of file bytes |
| `indexer/ast_parser.py::load_cached_nodes` | function | Loads ASTNode list from JSON cache if exists |
| `indexer/ast_parser.py::save_cached_nodes` | function | Saves ASTNode list as JSON to cache file |
| `indexer/cli.py::main` | function | Defines the root CLI command group via click.group |
| `indexer/cli.py::init` | function | Creates config, installs pre-commit hook, appends to CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes codebase: parses files, generates wiki pages, caches nodes |
| `indexer/cli.py::status` | function | Displays last indexed commit, stale files, manifest stats |
| `indexer/cli.py::hook` | function | Defines the hook subcommand group for managing pre-commit hook |
| `indexer/cli.py::hook_install` | function | Installs the pre-commit hook in current git repository |
| `indexer/cli.py::hook_remove` | function | Removes the pre-commit hook from current git repository |
| `indexer/cli.py::serve` | function | Starts MCP server for semantic code search over indexed wiki |
| `indexer/cli.py::serve_api` | function | Starts REST API server for remote semantic code search across repos |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Adds cache directory to .gitignore if missing |
| `indexer/cli.py::_is_indexable` | function | Checks if file path matches indexable pattern (not ignored) |
| `indexer/config.py::EmbeddingConfig` | class | Dataclass holding embedding model configuration parameters |
| `indexer/config.py::VectorStoreConfig` | class | Dataclass holding vector store configuration parameters |
| `indexer/config.py::Config` | class | Main configuration dataclass combining all settings |
| `indexer/config.py::_env` | function | Reads environment variable with default fallback |
| `indexer/config.py::_env_int` | function | Reads integer environment variable with default fallback |
| `indexer/config.py::load_config` | function | Loads and parses .indexer.toml into Config object |
| `indexer/config.py::_apply_env` | function | Overrides config fields with environment variable values |
| `indexer/config.py::save_config` | function | Saves Config object to .indexer.toml file |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves embedding API key from env or .env file |
| `indexer/embedding.py::_build_text` | function | Builds concatenated text string from ASTNode for embedding |
| `indexer/embedding.py::embed_nodes` | function | Embeds multiple ASTNodes concurrently using OpenAI API |
| `indexer/embedding.py::embed_query` | function | Embeds a single query string via embedding API |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI API to create embeddings for given texts |
| `indexer/git.py::_run` | function | Runs git command, returns stripped stdout |
| `indexer/git.py::current_commit` | function | Returns current Git commit hash via rev-parse HEAD |
| `indexer/git.py::current_branch` | function | Returns current Git branch name via branch --show-current |
| `indexer/git.py::staged_files` | function | Returns list of staged files via diff --cached --name-only |
| `indexer/git.py::changed_files_since` | function | Returns files changed since a given commit |
| `indexer/git.py::all_tracked_files` | function | Returns all tracked files via git ls-files |
| `indexer/git.py::is_git_repo` | function | Checks if path is inside a Git repository |
| `indexer/go_parser.py::_get_go_language` | function | Loads and returns tree-sitter Go language object |
| `indexer/go_parser.py::_extract_go_doc` | function | Extracts Go doc comment from preceding comments |
| `indexer/go_parser.py::_extract_imports` | function | Extracts import paths from Go source AST |
| `indexer/go_parser.py::_extract_calls` | function | Extracts target names of call expressions in Go AST |
| `indexer/go_parser.py::_get_receiver` | function | Extracts receiver type string from Go method definition |
| `indexer/go_parser.py::_get_name` | function | Extracts name of Go function or method definition |
| `indexer/go_parser.py::parse_go_file` | function | Parses Go source file into ASTNode objects via tree-sitter |
| `indexer/go_parser.py::visit` | function | Recursively walks Go AST nodes to extract structure or calls |
| `indexer/go_parser.py::visit` | function | Recursively walks Go AST nodes to extract structure or calls |
| `indexer/go_parser.py::visit` | function | Recursively walks Go AST nodes to extract structure or calls |
| `indexer/grouper.py::density_group` | function | Groups file paths into clusters based on directory density |
| `indexer/grouper.py::folder_of` | function | Returns parent directory string of a file path |
| `indexer/grouper.py::prefixes` | function | Generates all directory prefixes of a file path |
| `indexer/grouper.py::resolve_group` | function | Determines group label for a set of file paths |
| `indexer/hooks.py::_hook_command` | function | Returns the command string for repo-wiki hook script |
| `indexer/hooks.py::_hook_script_fresh` | function | Returns fresh hook script content |
| `indexer/hooks.py::_hook_script_append` | function | Returns hook script block to append to existing hooks |
| `indexer/hooks.py::install_hook` | function | Installs or updates the pre-commit hook script |
| `indexer/hooks.py::remove_hook` | function | Removes repo-wiki managed portion of pre-commit hook |
| `indexer/indexing.py::cross_reference` | function | Builds reverse dependency mapping between symbol IDs |
| `indexer/indexing.py::load_existing_nodes` | function | Loads previously parsed nodes from cache for changed files |
| `indexer/indexing.py::parse_candidates` | function | Parses candidate files, reusing cached nodes for unchanged ones |
| `indexer/indexing.py::build_batches` | function | Splits nodes into batches for parallel embedding |
| `indexer/indexing.py::write_wiki_pages` | function | Generates and writes wiki pages for each symbol group |
| `indexer/indexing.py::write_index_and_skill` | function | Writes main index page and skill documentation file |
| `indexer/indexing.py::update_manifest` | function | Updates manifest with current commit and file entries |
| `indexer/indexing.py::upsert_vectors` | function | Embeds and upserts vectors for changed files, deletes removed |
| `indexer/java_parser.py::_get_java_language` | function | Loads and returns tree-sitter Java language object |
| `indexer/java_parser.py::_extract_javadoc` | function | Extracts Javadoc comment text from preceding block |
| `indexer/java_parser.py::_extract_imports` | function | Extracts import statements from Java AST |
| `indexer/java_parser.py::_extract_calls` | function | Extracts method call targets from Java AST |
| `indexer/java_parser.py::_get_name` | function | Extracts name text from AST node's name child field |
| `indexer/java_parser.py::_get_type_name` | function | Extracts type name text from AST node's type child field |
| `indexer/java_parser.py::parse_java_file` | function | Parses Java file into AST, extracts symbols, imports, calls, javadoc |
| `indexer/java_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and javadoc |
| `indexer/java_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and javadoc |
| `indexer/java_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and javadoc |
| `indexer/js_parser.py::_get_language` | function | Determines JavaScript/TypeScript language object based on file extension |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts JSDoc comment text from AST node, cleans whitespace |
| `indexer/js_parser.py::_extract_imports` | function | Extracts import statements from AST, returns list of imported modules |
| `indexer/js_parser.py::_extract_calls` | function | Extracts function calls from AST subtree, returns set of called names |
| `indexer/js_parser.py::_get_name` | function | Extracts identifier name text from AST node's name child |
| `indexer/js_parser.py::parse_js_file` | function | Parses JS file into AST, extracts symbols, imports, calls, JSDoc |
| `indexer/js_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and JSDoc |
| `indexer/js_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and JSDoc |
| `indexer/js_parser.py::visit` | function | Recursively visits AST nodes to collect symbols, calls, and JSDoc |
| `indexer/llm.py::_is_anthropic` | function | Checks if model string starts with 'claude' or 'anthropic' |
| `indexer/llm.py::_resolve_api_key` | function | Resolves API key from env or config, uppercases env var name |
| `indexer/llm.py::_litellm_kwargs` | function | Returns LiteLLM completion kwargs including API key and model |
| `indexer/llm.py::_litellm_completion` | function | Calls LiteLLM completion with retry and exponential backoff |
| `indexer/llm.py::_anthropic_completion` | function | Calls Anthropic SDK completion with retry and exponential backoff |
| `indexer/llm.py::_should_use_anthropic_sdk` | function | Returns True if model is Anthropic via _is_anthropic |
| `indexer/llm.py::_parse_llm_json` | function | Parses LLM response JSON, recovers from truncation and malformed output |
| `indexer/llm.py::describe_nodes_batch` | function | Sends batch of node descriptions to LLM, parses JSON response |
| `indexer/llm.py::describe_nodes` | function | Describes multiple nodes concurrently using ThreadPoolExecutor |
| `indexer/llm.py::describe_files` | function | Sends file description batch to LLM, returns summarized descriptions |
| `indexer/llm.py::deep_enrich_page` | function | Deeply enriches a single page's symbols using LLM with context |
| `indexer/llm.py::deep_enrich_pages` | function | Deeply enriches multiple pages concurrently using ThreadPoolExecutor |
| `indexer/llm.py::deep_enrich_index` | function | Deeply enriches entire index using LLM with symbol context |
| `indexer/llm.py::rewrite_query` | function | Rewrites user query using LLM for improved search, returns list |
| `indexer/llm.py::synthesize_commit_message` | function | Generates commit message from diff using LLM |
| `indexer/manifest.py::FileEntry` | class | Represents a file entry with path and hash in the manifest |
| `indexer/manifest.py::Manifest` | class | Represents the codebase manifest with file entries and root path |
| `indexer/manifest.py::Manifest.stale_files` | method | Returns list of files whose content hash has changed |
| `indexer/manifest.py::Manifest.removed_files` | method | Returns list of files that no longer exist on disk |
| `indexer/manifest.py::compute_hash` | function | Computes SHA256 hash of file content as hex string |
| `indexer/manifest.py::load_manifest` | function | Loads manifest from JSON file, returns Manifest object |
| `indexer/manifest.py::save_manifest` | function | Saves manifest to JSON file, creates parent directories |
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Applies MCP server authentication middleware using API key header |
| `indexer/mcp_server.py::create_server` | function | Creates FastMCP server with search, trace, source tools |
| `indexer/mcp_server.py::create_api_server` | function | Creates FastMCP server backed by external API for repos |
| `indexer/mcp_server.py::_patched_method` | function | Patches HTTP method to check API key in request header |
| `indexer/mcp_server.py::search_symbols_tool` | function | MCP tool: search code symbols by semantic query, return results |
| `indexer/mcp_server.py::trace_call_tool` | function | MCP tool: trace call graph upstream or downstream from symbol |
| `indexer/mcp_server.py::get_source_context_tool` | function | MCP tool: read source code context around given lines |
| `indexer/mcp_server.py::_api_get` | function | Performs GET request to external API, returns parsed JSON |
| `indexer/mcp_server.py::_api_post` | function | Performs POST request to external API with JSON body |
| `indexer/mcp_server.py::list_repos` | function | MCP tool: list all registered repositories with stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | MCP tool: search code symbols by semantic query, return results |
| `indexer/mcp_server.py::trace_call_tool` | function | MCP tool: trace call graph upstream or downstream from symbol |
| `indexer/mcp_server.py::get_source_context_tool` | function | MCP tool: read source code context around given lines |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware that validates authorization and dispatches requests |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Validates auth header, removes prefix, and returns JSON error or passes request |
| `indexer/rest_api.py::_get_repo_lock` | function | Creates and returns an asyncio Lock for repo-level synchronization |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for async task status, with automatic cleanup of expired tasks |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes an empty dictionary to store tasks |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks from the store based on timestamps |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with a UUID, records start time, returns ID |
| `indexer/rest_api.py::TaskStore.get` | method | Returns the status of a task by its ID or None |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task state and completion time in the store |
| `indexer/rest_api.py::_detect_default_branch` | function | Detects the default git branch using 'git branch -r' and filtering |
| `indexer/rest_api.py::RepoRegistry` | class | Manages registered repository configurations with persistent file storage |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Creates temporary directory for storing repo registry file |
| `indexer/rest_api.py::RepoRegistry._save` | method | Writes the registry dictionary as JSON to the storage file |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from file, validates defaults and returns dictionary |
| `indexer/rest_api.py::RepoRegistry.register` | method | Validates repo config, adds to registry, saves to file |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes a repository from the registry and saves |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repository configuration for given name or None |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names |
| `indexer/rest_api.py::register_repo` | function | Handles POST request to register a new repository, starts background indexing |
| `indexer/rest_api.py::task_status` | function | Returns JSON response with task status by ID |
| `indexer/rest_api.py::validate_repo` | function | Validates repository structure and returns file statistics and indexability |
| `indexer/rest_api.py::sync_repo` | function | Triggers a background sync task for a repository's changes |
| `indexer/rest_api.py::rebuild_repo` | function | Triggers a background rebuild task for a repository index |
| `indexer/rest_api.py::sync_all_branches` | function | Triggers background sync tasks across all branches of a repository |
| `indexer/rest_api.py::rebuild_all_branches` | function | Triggers background rebuild tasks across all branches of a repository |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Executes the full indexing pipeline: discover, describe, cross-reference, and write wiki |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock, clones repo, runs full indexing pipeline, saves config |
| `indexer/rest_api.py::_run_sync_task` | function | Acquires lock, pulls latest changes, runs incremental indexing pipeline |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock and runs inner register task, releases lock on completion |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, stores credentials, loads manifest, runs indexing and saves config |
| `indexer/rest_api.py::unregister_repo` | function | Handles POST request to unregister a repository |
| `indexer/rest_api.py::search_symbols` | function | Handles POST request to search symbols with query rewriting and call graph expansion |
| `indexer/rest_api.py::trace_call` | function | Handles POST request to trace call graph up or down from a symbol |
| `indexer/rest_api.py::get_source_context` | function | Handles POST request to return source code lines around a given range |
| `indexer/rest_api.py::list_repos` | function | Returns JSON list of registered repositories with commit info and webhook URL |
| `indexer/rest_api.py::health` | function | Returns JSON response indicating service readiness |
| `indexer/rest_api.py::repo_detail` | function | Returns JSON detail for a repository including file structure and webhook |
| `indexer/rest_api.py::multi_repo_skill` | function | Returns aggregated skill descriptions and file trees across multiple repositories |
| `indexer/rest_api.py::_get_webhook_url` | function | Builds webhook URL with HMAC-signed token for a given repository |
| `indexer/rest_api.py::_webhook_sign` | function | Creates HMAC-SHA256 hex digest of payload using secret |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Compares provided signature with computed HMAC digest using constant-time comparison |
| `indexer/rest_api.py::webhook_by_name` | function | Validates webhook signature and triggers background sync or rebuild tasks |
| `indexer/rest_api.py::create_app` | function | Creates and returns a Starlette ASGI app with all routes, middleware, and static files |
| `indexer/rest_api.py::_index_page` | function | Returns rendered HTML index page with repo data injected as JSON |
| `indexer/rest_api.py::_inject_credentials` | function | Embeds username/password into repository clone URL |
| `indexer/rest_api.py::_sanitize_error` | function | Removes sensitive paths from error messages by replacing with '***' |
| `indexer/rest_api.py::_store_credentials` | function | Writes parsed credentials to file with secure permissions. |
| `indexer/rest_api.py::_resolve_repos` | function | Fetches repository list from configuration dict. |
| `indexer/rest_api.py::_trace_call_impl` | function | Traces call chains by fetching and merging call graph IDs. |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands node list with call graph by fetching referenced IDs. |
| `indexer/rest_api.py::_parse_json_list` | function | Parses JSON string into a Python list. |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON request body into dict or list. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task based on mode. |
| `indexer/rest_api.py::_run_all` | function | Runs sync or rebuild task based on mode. |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that enforces authentication for API routes. |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Validates authentication token and forwards or rejects request. |
| `indexer/retrieval.py::search_symbols` | function | Searches for symbols using embedded query and expands with call graph. |
| `indexer/retrieval.py::trace_call` | function | Traces call graph for a given symbol ID. |
| `indexer/retrieval.py::get_source_context` | function | Reads source file and returns context lines around a location. |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Expands symbol list with IDs from call graph. |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON string to list. |
| `indexer/ruby_parser.py::_get_ruby_language` | function | Initializes and returns tree-sitter Ruby language object. |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function | Extracts Ruby documentation comments from AST node. |
| `indexer/ruby_parser.py::_extract_imports` | function | Extracts import statements from Ruby AST via visitor. |
| `indexer/ruby_parser.py::_extract_calls` | function | Extracts function call names from Ruby AST. |
| `indexer/ruby_parser.py::_get_name` | function | Returns node name by extracting child's text. |
| `indexer/ruby_parser.py::parse_ruby_file` | function | Parses Ruby source file into structured AST nodes with metadata. |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, extracting symbols and metadata. |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, extracting symbols and metadata. |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, extracting symbols and metadata. |
| `indexer/rust_parser.py::_get_rust_language` | function | Initializes and returns tree-sitter Rust language object. |
| `indexer/rust_parser.py::_extract_rust_doc` | function | Extracts Rust doc comments from node. |
| `indexer/rust_parser.py::_extract_imports` | function | Extracts imports from Rust AST. |
| `indexer/rust_parser.py::_extract_calls` | function | Extracts function calls from Rust AST. |
| `indexer/rust_parser.py::_get_name` | function | Gets node name from child field. |
| `indexer/rust_parser.py::parse_rust_file` | function | Parses Rust file into AST nodes with doc, imports, calls. |
| `indexer/rust_parser.py::visit` | function | Recursively visits Rust AST nodes. |
| `indexer/rust_parser.py::visit` | function | Recursively visits Rust AST nodes. |
| `indexer/rust_parser.py::visit` | function | Recursively visits Rust AST nodes. |
| `indexer/utils.py::_rel` | function | Converts absolute path to relative path string. |
| `indexer/utils.py::_node_text` | function | Decodes tree-sitter node bytes to string. |
| `indexer/utils.py::load_env_file` | function | Reads and parses .env file into environment variables. |
| `indexer/vector_store.py::_get_client` | function | Creates and returns persistent Chroma vector client. |
| `indexer/vector_store.py::_get_or_create_collection` | function | Gets or creates a Chroma collection by name. |
| `indexer/vector_store.py::upsert_nodes` | function | Upserts document nodes into vector store with metadata. |
| `indexer/vector_store.py::search` | function | Queries vector store for similar nodes using embedding. |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves vector store items by their IDs. |
| `indexer/vector_store.py::delete_by_files` | function | Deletes vector store entries by associated file paths. |
| `indexer/vector_store.py::_build_doc` | function | Builds document string from node name and signature. |
| `indexer/vector_store.py::_build_meta` | function | Builds JSON-compacted metadata for vector storage. |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes dict to compact JSON string. |
| `indexer/wiki.py::PageContext` | class | Data class holding page context for wiki generation. |
| `indexer/wiki.py::IndexEntry` | class | Data class representing a single index entry. |
| `indexer/wiki.py::_jinja_env` | function | Creates Jinja2 environment with file system loader. |
| `indexer/wiki.py::build_page` | function | Renders a wiki page from template using symbol groups. |
| `indexer/wiki.py::build_index` | function | Renders index page from template. |
| `indexer/wiki.py::sanitize_group_label` | function | Sanitizes group label for file-safe string. |
| `indexer/wiki.py::write_page` | function | Writes rendered wiki page to file, creating directories. |
| `indexer/wiki.py::write_index` | function | Writes rendered index to file, creating directory. |
## Data Flows
- CLI `run` → parse each indexable file → extract ASTNodes → compute hash → cache JSON → embed nodes → generate wiki pages → update manifest
- CLI `serve` (MCP) → incoming query → vector store search (by embedding) → retrieve top-k ASTNodes → format context → return to LLM client
- CLI `serve-api` (REST) → POST request with repo path → clone/index remote repo (if not cached) → build vector store → respond with search results
- Pre-commit hook → `run --commit` → detect changed files → re-parse only modified → update wiki and manifest
## Design Constraints
- File hash (SHA256) determines re-parse need; unchanged files use cached ASTNode JSON to avoid redundant computation.
- Embedding API key resolved via environment variable or .env file; if absent, embedding step silently skips (nodes stored without vectors).
- ASTNode cache is stored in `.indexer/cache/<file_hash>.json`; cache directory auto-added to `.gitignore` on `init`.
- Language-specific parser selection is based on file extension (e.g., `.py` → python parser, `.js` → js_parser); unsupported extensions are ignored by `_is_indexable`.
- Indexable files filtered by `ignore` globs in `.indexer.toml`; dot-directories and common build artifacts excluded by default.
- Vector store (ChromaDB) is ephemeral per index run; wiki markdown pages are the persistent searchable artifact, not the vector DB.
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, Environment, FastMCP, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, OpenAI, PageContext, Parser, Path, PersistentClient, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _anthropic_completion, _api_get, _api_post, _apply_env, _apply_mcp_auth, _build_doc, _build_meta, _build_text, _call_embedding_api, _cleanup, _detect_default_branch, _ensure_cache_gitignore, _env, _env_int, _expand_with_call_graph, _extract_calls, _extract_go_doc, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _extract_rust_doc, _get_class_method_ids, _get_client, _get_go_language, _get_java_language, _get_language, _get_name, _get_or_create_collection, _get_receiver, _get_repo_lock, _get_ruby_language, _get_rust_language, _get_webhook_url, _hook_command, _hook_script_append, _hook_script_fresh, _inject_credentials, _is_anthropic, _is_indexable, _jinja_env, _litellm_completion, _litellm_kwargs, _node_text, _orig_method, _parse_body, _parse_json_list, _parse_llm_json, _rel, _resolve_api_key, _resolve_repos, _run, _run_indexing_pipeline, _run_rebuild_task, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _verify_webhook_sign, _webhook_sign, acquire, add, add_middleware, all, all_tracked_files, any, append, as_completed, asdict, body, build_batches, build_index, build_page, call_next, changed_files_since, child_by_field_name, chmod, command, compare_digest, completion, compute_hash, compute_hash_short, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, decode, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, describe_files, describe_nodes, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, exists, extend, fnmatch, folder_of, get, get_by_ids, get_docstring, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, glob, group, hasattr, hexdigest, id, info, install_hook, int, is_dir, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_names, load, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_file, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, prefixes, progress_callback, query, quote, range, read, read_bytes, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_group, result, rewrite_query, rfind, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, tool, trace_call, uniform, unlink, unregister, update, update_manifest, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/indexing.py::load_existing_nodes, indexer/indexing.py::parse_candidates, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/indexing.py::write_wiki_pages, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_litellm_completion, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_files, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::load_manifest, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::RepoRegistry.register, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::write_page, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_page, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.vector_store.delete_by_files, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.OpenAI, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.middleware.trustedhost.TrustedHostMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_go, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_rust, tree_sitter_typescript, typing.Optional, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
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
- `upsert_nodes`
- `delete_by_files`
