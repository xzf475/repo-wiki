# indexer/

## Overview

The indexer module provides automated codebase indexing for semantic search and documentation. It parses source files (Python, JS, Java, Ruby) via `ast_parser.py` and language-specific parsers into `ASTNode` objects, extracts call graphs and docstrings, and generates wiki pages (`wiki.py`). Embeddings of code entities are created via `embedding.py` (using OpenAI) and stored in a configurable vector store (`vector_store.py`, e.g., Chroma). The CLI (`cli.py`) orchestrates incremental indexing based on git changes, manages caching, and serves the index via both MCP (`mcp_server.py`) and REST (`rest_api.py`) APIs. Configuration lives in `config.py` (TOML + env overrides) and persists in a per-repo cache directory.

## Modules
| File | Purpose |
|------|---------|
| indexer/embedding.py | OpenAI embedding generation for code nodes |
| indexer/grouper.py | Grouping files by directory or density |
| indexer/js_parser.py | JavaScript/TypeScript source code parser |
| indexer/ast_parser.py | Python AST parser for code symbol extraction |
| indexer/ruby_parser.py | Ruby source code parser using tree-sitter |
| indexer/mcp_server.py | MCP server for semantic code search |
| indexer/indexing.py | Core indexing pipeline and wiki generation |
| indexer/wiki.py | Wiki page and index generation from nodes |
| indexer/java_parser.py | Java source code parser using tree-sitter |
| indexer/cli.py | Command-line interface for indexing and serving |
| indexer/llm.py | LLM-powered node and file description generation |
| indexer/manifest.py | File manifest tracking and hashing |
| indexer/vector_store.py | ChromaDB vector store for embeddings |
| indexer/retrieval.py | Semantic search and call graph tracing |
| indexer/config.py | Configuration loading and saving for indexing |
| indexer/hooks.py | Pre-commit hook installation and removal |
| indexer/rest_api.py | REST API for multi-repo indexing and management |
| indexer/utils.py | Utility functions for relative paths and env |
| indexer/git.py | Git repository operations and file tracking |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class | Represents a parsed symbol with ID, type, docstring, calls, and line range |
| `indexer/ast_parser.py::_extract_imports` | function | Walks AST nodes to collect imported module names |
| `indexer/ast_parser.py::_extract_calls` | function | Traverses AST to collect all function call names |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Walks class body to collect IDs of methods defined inside |
| `indexer/ast_parser.py::parse_file` | function | Parses Python/JS/Java files, extracts imports, calls, docstrings, returns node list |
| `indexer/ast_parser.py::compute_hash_short` | function | Reads file bytes and returns first 8 hex chars of SHA256 hash |
| `indexer/ast_parser.py::load_cached_nodes` | function | Reads and deserializes cached ASTNode list from JSON file |
| `indexer/ast_parser.py::save_cached_nodes` | function | Serializes and writes ASTNode list to cache directory as JSON |
| `indexer/cli.py::main` | function | Entry point for indexer CLI, groups subcommands |
| `indexer/cli.py::init` | function | Creates config file, installs pre-commit hook, appends to CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes changed files, generates wiki pages, updates vector store |
| `indexer/cli.py::status` | function | Displays last commit, stale files, and manifest statistics |
| `indexer/cli.py::hook` | function | Group command for install/remove pre-commit hook |
| `indexer/cli.py::hook_install` | function | Installs repo-wiki pre-commit hook in current repository |
| `indexer/cli.py::hook_remove` | function | Removes repo-wiki pre-commit hook script from repo |
| `indexer/cli.py::serve` | function | Starts repo-wiki MCP server for semantic code search via MCP |
| `indexer/cli.py::serve_api` | function | Starts REST API server for multi-repo semantic code search |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Adds cache directory to .gitignore if missing |
| `indexer/cli.py::_is_indexable` | function | Returns True if file path matches indexable patterns, False otherwise |
| `indexer/config.py::EmbeddingConfig` | class | Dataclass holding embedding model, dimensions, and API settings |
| `indexer/config.py::VectorStoreConfig` | class | Dataclass for vector store type, path, and dimension settings |
| `indexer/config.py::Config` | class | Dataclass combining all config sections: embedding, store, llm, etc |
| `indexer/config.py::_env` | function | Reads environment variable by key, returns value or None |
| `indexer/config.py::_apply_env_field` | function | Sets config field from environment variable if defined |
| `indexer/config.py::_env_int` | function | Reads environment variable as int, warns on invalid value |
| `indexer/config.py::load_config` | function | Loads TOML config file, applies env overrides, returns Config object |
| `indexer/config.py::_apply_env` | function | Iterates config sections and applies environment variable overrides |
| `indexer/config.py::save_config` | function | Writes config dict to TOML file using atomic write |
| `indexer/embedding.py::_get_openai_client` | function | Creates and returns OpenAI client with configured API key |
| `indexer/embedding.py::_resolve_api_key` | function | Loads API key from environment variables or .env file |
| `indexer/embedding.py::_build_text` | function | Builds string from node ID, type, docstring, and calls for embedding |
| `indexer/embedding.py::embed_nodes` | function | Embeds node texts using ThreadPoolExecutor, returns node-vector pairs |
| `indexer/embedding.py::embed_query` | function | Embeds a query string into a vector for semantic search |
| `indexer/embedding.py::_call_embedding_api` | function | Calls OpenAI embedding API with exponential backoff and batching |
| `indexer/git.py::_run` | function | Executes git command, strips output, returns string or False on failure |
| `indexer/git.py::current_commit` | function | Returns SHA of HEAD commit via git rev-parse |
| `indexer/git.py::current_branch` | function | Returns current branch name via git rev-parse |
| `indexer/git.py::staged_files` | function | Returns list of files staged for commit via git diff |
| `indexer/git.py::changed_files_since` | function | Returns list of files modified since given commit ref |
| `indexer/git.py::all_tracked_files` | function | Returns list of all files tracked by git in the repo |
| `indexer/git.py::is_git_repo` | function | Returns True if current directory is a git repository |
| `indexer/grouper.py::density_group` | function | Groups file paths into clusters based on directory density |
| `indexer/grouper.py::folder_of` | function | Returns parent directory string of a given file path |
| `indexer/grouper.py::prefixes` | function | Returns list of all directory prefixes for a file path |
| `indexer/grouper.py::resolve_group` | function | Finds the best group for a file based on density and prefix similarity |
| `indexer/hooks.py::_hook_command` | function | Builds the CLI command string for the pre-commit hook |
| `indexer/hooks.py::_hook_script_fresh` | function | Generates full pre-commit hook script for first install |
| `indexer/hooks.py::_hook_script_append` | function | Generates the repo-wiki block to append to existing hooks |
| `indexer/hooks.py::install_hook` | function | Installs or updates repo-wiki pre-commit hook with config command |
| `indexer/hooks.py::remove_hook` | function | Removes the repo-wiki managed block from pre-commit hook |
| `indexer/indexing.py::cross_reference` | function | Builds bidirectional call graph mapping from node list |
| `indexer/indexing.py::load_existing_nodes` | function | Loads existing nodes from cache, returns list with updated hashes |
| `indexer/indexing.py::parse_candidates` | function | Parses new/changed files, caches nodes, returns parsed node list |
| `indexer/indexing.py::build_batches` | function | Groups nodes into batches of given size for LLM description |
| `indexer/indexing.py::write_wiki_pages` | function | Writes wiki pages for each file group with symbol descriptions |
| `indexer/indexing.py::write_index_and_skill` | function | Generates index page and skill template from wiki pages |
| `indexer/indexing.py::update_manifest` | function | Updates manifest with current commit, file hashes, and timestamps |
| `indexer/indexing.py::upsert_vectors` | function | Embeds changed files and upserts vectors, removes deleted files |
| `indexer/java_parser.py::_get_java_language` | function | Returns tree-sitter Language object for Java parsing |
| `indexer/java_parser.py::_extract_javadoc` | function | Extracts and cleans Javadoc comment string from AST node |
| `indexer/java_parser.py::_extract_imports` | function | Visits import_declaration nodes to collect package names |
| `indexer/java_parser.py::_extract_calls` | function | Visits method_invocation nodes to collect called method names |
| `indexer/java_parser.py::_get_name` | function | Returns the name child text of a named Java AST node |
| `indexer/java_parser.py::_get_type_name` | function | Returns the type child text of a Java AST node |
| `indexer/java_parser.py::parse_java_file` | function | Parses Java source, extracts imports, calls, docstrings, returns nodes |
| `indexer/java_parser.py::visit` | function | Visits class and method declarations, extracts name, doc, calls, returns node |
| `indexer/java_parser.py::visit` | function | Visits class and method declarations, extracts name, doc, calls, returns node |
| `indexer/java_parser.py::visit` | function | Visits class and method declarations, extracts name, doc, calls, returns node |
| `indexer/js_parser.py::_get_language` | function | Returns tree-sitter Language for JavaScript, TypeScript, or TSX |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts and cleans JSDoc comment string from AST node |
| `indexer/js_parser.py::_extract_imports` | function | Visits import_statement nodes to collect module source names |
| `indexer/js_parser.py::_extract_calls` | function | Visits call_expression nodes to collect called function names |
| `indexer/js_parser.py::_get_name` | function | Returns the name child text of a named JS AST node |
| `indexer/js_parser.py::parse_js_file` | function | Parses JavaScript/TypeScript source, extracts imports, calls, docstrings |
| `indexer/js_parser.py::visit` | function | Visits function/class declarations, extracts name, doc, calls |
| `indexer/js_parser.py::visit` | function | Visits function/class declarations, extracts name, doc, calls |
| `indexer/js_parser.py::visit` | function | Visits function/class declarations, extracts name, doc, calls |
| `indexer/llm.py::_EmptyResponseError` | class | Custom exception raised when LLM returns empty response |
| `indexer/llm.py::_is_anthropic` | function | Returns True if model string starts with 'claude' or 'anthropic' |
| `indexer/llm.py::_resolve_api_key` | function | Loads API key from environment variable or .env file for LLM |
| `indexer/llm.py::_litellm_kwargs` | function | Builds extra kwargs dict for litellm completion calls |
| `indexer/llm.py::_litellm_completion` | function | Calls litellm completion API with exponential backoff and validation |
| `indexer/llm.py::_get_anthropic_client` | function | Creates and returns Anthropic client with API key |
| `indexer/llm.py::_anthropic_completion` | function | Calls Anthropic messages API with exponential backoff and validation |
| `indexer/llm.py::_should_use_anthropic_sdk` | function | Returns True if model is Anthropic and SDK should be used |
| `indexer/llm.py::_parse_llm_json` | function | Parses LLM response JSON, recovering from truncation and malformed output |
| `indexer/llm.py::describe_nodes_batch` | function | Sends batch of node specs to LLM, returns descriptions dict |
| `indexer/llm.py::describe_nodes` | function | Describes multiple node batches concurrently using ThreadPoolExecutor |
| `indexer/llm.py::describe_files` | function | Sends file content summaries to LLM, returns file descriptions |
| `indexer/llm.py::deep_enrich_page` | function | Sends page content to LLM for deep enrichment, returns enriched page data |
| `indexer/llm.py::deep_enrich_pages` | function | Enriches multiple wiki pages via threaded LLM calls |
| `indexer/llm.py::deep_enrich_index` | function | Sends index page content to LLM for deep enrichment |
| `indexer/llm.py::rewrite_query` | function | Sends query to LLM for rewriting into multiple search variants |
| `indexer/llm.py::synthesize_commit_message` | function | Sends diff summary to LLM, returns synthesized commit message |
| `indexer/manifest.py::FileEntry` | class | Dataclass holding file path and hash for manifest tracking |
| `indexer/manifest.py::Manifest` | class | Dataclass containing commit, timestamp, and file entries map |
| `indexer/manifest.py::Manifest.stale_files` | method | Returns list of files whose stored hash doesn't match current file |
| `indexer/manifest.py::Manifest.removed_files` | method | Returns list of files in manifest that no longer exist on disk |
| `indexer/manifest.py::compute_hash` | function | Reads file and returns full SHA256 hex digest string |
| `indexer/manifest.py::load_manifest` | function | Reads and deserializes Manifest from JSON file, handles missing keys |
| `indexer/manifest.py::save_manifest` | function | Serializes Manifest to JSON and writes atomically via temp file |
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Wraps MCP tools with authentication check from config |
| `indexer/mcp_server.py::create_server` | function | Creates FastMCP server with search, trace, and source context tools |
| `indexer/mcp_server.py::create_api_server` | function | Creates FastMCP server that proxies requests to remote API endpoints |
| `indexer/mcp_server.py::_patched_method` | function | Decorator that checks auth header before executing original method |
| `indexer/mcp_server.py::search_symbols_tool` | function | Semantic code search across one or all repos, supports query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph across repos with repo specification |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code lines around given file and line range |
| `indexer/mcp_server.py::_api_request` | function | Sends HTTP request to external API and returns parsed JSON response |
| `indexer/mcp_server.py::_api_get` | function | Sends HTTP GET request via _api_request |
| `indexer/mcp_server.py::_api_post` | function | Sends HTTP POST request via _api_request with JSON body |
| `indexer/mcp_server.py::list_repos` | function | Lists all registered repositories with descriptions and stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | Semantic code search across one or all repos, supports query rewriting |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call graph across repos with repo specification |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code lines around given file and line range |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | Starlette middleware that validates a static API token |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Checks Authorization header against token, returns 401 or passes request |
| `indexer/rest_api.py::_get_repo_lock` | function | Creates a threading Lock for a given repo name |
| `indexer/rest_api.py::TaskStore` | class | In-memory store for async task status with expiration cleanup |
| `indexer/rest_api.py::TaskStore.__init__` | method | Initializes empty task dict and Lock for thread safety |
| `indexer/rest_api.py::TaskStore._cleanup` | method | Removes expired tasks older than 5 minutes, keeps up to 100 |
| `indexer/rest_api.py::TaskStore.create` | method | Creates a new task with UUID, returns task ID |
| `indexer/rest_api.py::TaskStore.get` | method | Returns task dict by ID |
| `indexer/rest_api.py::TaskStore.update` | method | Updates task status and timestamp |
| `indexer/rest_api.py::_detect_default_branch` | function | Runs git to find default branch name from remote |
| `indexer/rest_api.py::_match_branch_rule` | function | Checks branch name against fnmatch patterns in comma-separated rule |
| `indexer/rest_api.py::_discover_remote_branches` | function | Fetches remote branches matching glob patterns via git ls-remote |
| `indexer/rest_api.py::RepoRegistry` | class | Persistent registry of repositories with JSON file storage |
| `indexer/rest_api.py::RepoRegistry.__init__` | method | Initializes registry with temp directory, RLock, and loads saved state |
| `indexer/rest_api.py::RepoRegistry._save` | method | Writes registry data to temporary file then replaces main JSON atomically |
| `indexer/rest_api.py::RepoRegistry._load` | method | Loads registry from JSON file, detects default branches, returns dict |
| `indexer/rest_api.py::RepoRegistry.register` | method | Adds repo with config, saves to file |
| `indexer/rest_api.py::RepoRegistry.unregister` | method | Removes repo from registry and saves |
| `indexer/rest_api.py::RepoRegistry.get` | method | Returns repo config dict by name |
| `indexer/rest_api.py::RepoRegistry.list_names` | method | Returns sorted list of registered repo names |
| `indexer/rest_api.py::RepoRegistry.items` | method | Returns list of name-config tuples |
| `indexer/rest_api.py::RepoRegistry.update_meta` | method | Updates repo meta fields and triggers _save |
| `indexer/rest_api.py::register_repo` | function | HTTP endpoint that parses body, discovers branches, creates indexing task |
| `indexer/rest_api.py::task_status` | function | HTTP endpoint returning task store items filtered by repo prefix |
| `indexer/rest_api.py::validate_repo` | function | HTTP endpoint that validates repo state and index consistency |
| `indexer/rest_api.py::sync_repo` | function | HTTP endpoint that triggers incremental sync task for a repo |
| `indexer/rest_api.py::rebuild_repo` | function | HTTP endpoint that triggers full rebuild task for a repo |
| `indexer/rest_api.py::sync_all_branches` | function | HTTP endpoint that syncs all branches of a repo with lock |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, rediscover branches, rebuilds all branches |
| `indexer/rest_api.py::rebuild_all_branches` | function | HTTP endpoint that rebuilds all branches of a repo with lock |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Orchestrates full indexing: parse, enrich, cross-reference, write index |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires repo lock and runs rebuild inner task |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Performs full clone, checkout, parse, index, and skill generation |
| `indexer/rest_api.py::_run_sync_task` | function | Incremental sync: detects changed files, rebuilds index for them |
| `indexer/rest_api.py::_run_register_task` | function | Acquires repo lock and runs register inner task |
| `indexer/rest_api.py::_run_register_task_inner` | function | Full registration: clone, parse, index, write webhook config |
| `indexer/rest_api.py::unregister_repo` | function | HTTP endpoint that unregisters a repo by name |
| `indexer/rest_api.py::search_symbols` | function | Searches vector store and expands results with call graph |
| `indexer/rest_api.py::trace_call` | function | Traces call chain from a symbol to callers and callees |
| `indexer/rest_api.py::get_source_context` | function | Returns source code lines with padding for a given file range |
| `indexer/rest_api.py::list_repos` | function | Lists registered repos with commit and webhook URL |
| `indexer/rest_api.py::health` | function | Returns 'ok' with registered repo count |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repo info including branches and files |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repo metadata fields |
| `indexer/rest_api.py::multi_repo_skill` | function | Collects and returns aggregated skill files from multiple repos |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook URL from base URL and repo name with signature |
| `indexer/rest_api.py::_webhook_sign` | function | Creates HMAC-SHA256 signature of body using secret key |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Compares provided signature with computed HMAC digest |
| `indexer/rest_api.py::webhook_by_name` | function | Handles incoming webhook events, triggers appropriate tasks |
| `indexer/rest_api.py::create_app` | function | Builds Starlette application with routes, middleware, and static files |
| `indexer/rest_api.py::_index_page` | function | Serves HTML index page with embedded JSON data |
| `indexer/rest_api.py::_inject_credentials` | function | Inserts authentication credentials into a URL for git clone |
| `indexer/rest_api.py::_sanitize_error` | function | Removes sensitive paths and tokens from error messages |
| `indexer/rest_api.py::_store_credentials` | function | Writes git credentials helper config to cache directory |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo names from request query or all registered repos |
| `indexer/rest_api.py::_trace_call_impl` | function | Recursively builds call graph by querying vector store |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands search results with called and caller symbols |
| `indexer/rest_api.py::_parse_json_list` | function | Parses JSON string to list, returns empty list on failure |
| `indexer/rest_api.py::_InvalidBodyError` | class | Custom exception for invalid request body |
| `indexer/rest_api.py::_parse_body` | function | Parses and validates request JSON body, returns dict or raises error |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs sync task for all repos |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs sync task for all repos |
| `indexer/rest_api.py::_run_all` | function | Acquires repo lock and runs sync task for all repos |
| `indexer/rest_api.py::_LoggingMiddleware` | class | Starlette middleware that logs request method, path, and duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request start and completion with elapsed time |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns JSON 400 response with error message from exception |
| `indexer/rest_api.py::_AuthMiddleware` | class | Starlette middleware that validates API token from X-API-Key header |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks X-API-Key header against token, returns 401 if mismatch |
| `indexer/retrieval.py::search_symbols` | function | Searches vector store with query embedding and expands with call graph |
| `indexer/retrieval.py::trace_call` | function | Traces call chain from a symbol by querying vector store recursively |
| `indexer/retrieval.py::get_source_context` | function | Reads source file lines with padding, returns formatted text |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Expands result set with called or caller symbols from vector store |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON list from string, returns empty list on error |
| `indexer/ruby_parser.py::_get_ruby_language` | function | Returns tree-sitter Language object for Ruby |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function | Extracts and cleans Ruby doc comment from node text |
| `indexer/ruby_parser.py::_extract_imports` | function | Recursively finds require and require_relative declarations in AST |
| `indexer/ruby_parser.py::_extract_calls` | function | Recursively finds method calls (send nodes) in AST |
| `indexer/ruby_parser.py::_get_name` | function | Extracts name string from a Ruby AST node |
| `indexer/ruby_parser.py::parse_ruby_file` | function | Parses Ruby file using tree-sitter, returns list of ASTNode objects |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, collecting imports or calls based on context |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, collecting imports or calls based on context |
| `indexer/ruby_parser.py::visit` | function | Recursively visits AST nodes, collecting imports or calls based on context |
| `indexer/utils.py::_rel` | function | Converts absolute path to repository-relative path |
| `indexer/utils.py::_node_text` | function | Decodes node text from bytes to string |
| `indexer/utils.py::load_env_file` | function | Loads environment variables from .env file in project root |
| `indexer/vector_store.py::_get_client` | function | Returns persistent ChromaDB client instance |
| `indexer/vector_store.py::_get_or_create_collection` | function | Gets or creates a ChromaDB collection by name |
| `indexer/vector_store.py::upsert_nodes` | function | Upserts document nodes into vector store with metadata |
| `indexer/vector_store.py::search` | function | Queries vector store by embedding, returns ranked results |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves vector store entries by ID list |
| `indexer/vector_store.py::delete_by_files` | function | Deletes vector store entries matching file paths |
| `indexer/vector_store.py::_build_doc` | function | Constructs a document text from node fields for embedding |
| `indexer/vector_store.py::_truncate_list` | function | Truncates a list of values to fit within token limits |
| `indexer/vector_store.py::_build_meta` | function | Builds metadata dict for a vector store entry |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes object to compact JSON string |
| `indexer/wiki.py::PageContext` | class | Data class holding page context for wiki rendering |
| `indexer/wiki.py::IndexEntry` | class | Data class for a wiki index entry with name and path |
| `indexer/wiki.py::_jinja_env` | function | Creates Jinja2 environment with file system loader and filters |
| `indexer/wiki.py::build_page` | function | Renders a single wiki page from template and context |
| `indexer/wiki.py::build_index` | function | Renders wiki index page from template |
| `indexer/wiki.py::sanitize_group_label` | function | Sanitizes a group label for use in file paths |
| `indexer/wiki.py::write_page` | function | Writes a rendered wiki page to disk |
| `indexer/wiki.py::write_index` | function | Writes rendered wiki index to disk |
## Data Flows
- `indexer run` → git diff finds changed files → `ast_parser` parses each → `wiki.py` writes/updates .md file → `embedding.py` embeds → `vector_store.py` upserts → `manifest.py` records commit hash
- MCP client sends query → `mcp_server.py` receives → `retrieval.py` loads vector store → returns top-k `ASTNode` references with wiki paths
- `indexer init` → creates config file → installs pre-commit hook (`hooks.py`) → appends to CLAUDE.md → ensures `.gitignore` caches
- `indexer serve --api` → `rest_api.py` creates Flask app → iterates repo directories → loads each index → accepts search queries via REST
## Design Constraints
- Parsing is cached by truncating file SHA256 to first 8 hex chars; cache miss only on content change, not timestamp.
- Language-specific parsers are switched by file extension/name string matching inside `ast_parser.parse_file`, not by config or heuristics beyond the provided patterns.
- The pre-commit hook runs `indexer run` on every commit; if indexing fails, the commit still proceeds (hook is non-blocking).
- API key for embeddings is resolved in order: `OPENAI_API_KEY` env var > `.env` file in repo root > `config.toml`; missing key silences embedding but indexing proceeds.
- Vector store dimension must match embedding model output dimension; mismatch causes silent insert failures (no validation at config load).
- The manifest (`manifest.json`) is the source of truth for which files have been indexed; stale files are detected by comparing current git hash vs stored hash, not by file mtime.
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, Environment, FastMCP, FileEntry, FileSystemLoader, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Parser, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _build_doc, _build_meta, _build_text, _call_embedding_api, _cleanup, _detect_default_branch, _discover_remote_branches, _ensure_cache_gitignore, _env, _env_int, _expand_with_call_graph, _extract_calls, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _get_anthropic_client, _get_class_method_ids, _get_client, _get_java_language, _get_language, _get_name, _get_openai_client, _get_or_create_collection, _get_repo_lock, _get_ruby_language, _get_webhook_url, _hook_command, _hook_script_append, _hook_script_fresh, _inject_credentials, _is_anthropic, _is_indexable, _jinja_env, _litellm_completion, _litellm_kwargs, _match_branch_rule, _node_text, _orig_method, _parse_body, _parse_json_list, _parse_llm_json, _rel, _resolve_api_key, _resolve_repos, _run, _run_indexing_pipeline, _run_rebuild_task, _run_rebuild_task_inner, _run_register_task_inner, _run_sync_task, _sanitize_error, _save, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, asdict, body, bool, build_batches, build_index, build_page, call_next, changed_files_since, child_by_field_name, chmod, command, compare_digest, completion, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, decode, deep_enrich_index, deep_enrich_pages, defaultdict, delete, density_group, describe_files, describe_nodes, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, exists, extend, fnmatch, folder_of, fromkeys, get, get_by_ids, get_collection, get_docstring, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, glob, group, hasattr, hexdigest, id, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_names, load, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_file, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, pop, prefixes, progress_callback, query, quote, range, read, read_bytes, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_group, result, rewrite_query, rfind, rglob, rmtree, rstrip, run, run_in_executor, sanitize_group_label, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sub, submit, sum, synthesize_commit_message, time, tool, trace_call, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, with_suffix, write, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/indexing.py::load_existing_nodes, indexer/indexing.py::parse_candidates, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/indexing.py::write_wiki_pages, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_anthropic_completion, indexer/llm.py::_litellm_completion, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_files, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::load_manifest, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/rest_api.py::RepoRegistry._load, indexer/rest_api.py::RepoRegistry.register, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_expand_with_call_graph, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::_trace_call_impl, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::write_page, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default, tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic, tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_page, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_typescript, typing.Optional, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
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
