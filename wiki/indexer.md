# indexer/

## Overview

The indexer module exists to parse multi-language source code into structured ASTNode objects, build a searchable vector index via embeddings, and expose symbol lookup, call tracing, and file grouping through an MCP (Model Context Protocol) server. Key classes include ASTNode (unified metadata with type, docstring, calls), grouper functions (density_group, folder_of, resolve_group) which cluster files by path prefix density rather than directory boundaries, and hooks.py which installs git pre-commit hooks to trigger incremental re-indexing. The module's architecture decouples language-specific parsers (ast_parser, go_parser, etc.) from a shared vector_store and retrieval module, enabling cross-language symbol searches and tracebacks consumed by AI agents via the MCP server (create_server, search_symbols_tool).

## Modules
| File | Purpose |
|------|---------|
| indexer/git_ops.py | Git branch management and credential injection operations |
| indexer/vector_store.py | Vector store client and collection management for indexing |
| indexer/git.py | Git repository querying and file tracking utilities |
| indexer/java_parser.py | Tree-sitter based parser for Java source code analysis |
| indexer/llm.py | LLM client abstraction for generating node and file descriptions |
| indexer/embedding.py | Generates and caches embeddings for AST nodes |
| indexer/repo_registry.py | Registry for managing repository locks and state |
| indexer/manifest.py | Manifest management with hashing and persistence for file tracking |
| indexer/ast_parser.py | Parses source code into AST nodes for indexing |
| indexer/retrieval.py | Retrieves relevant code symbols and source context |
| indexer/grouper.py |  |
| indexer/go_parser.py | Tree-sitter based parser for Go source code analysis |
| indexer/js_parser.py | Tree-sitter based parser for JavaScript source code analysis |
| indexer/rest_api.py | REST API for repository registration, sync, and reindexing |
| indexer/utils.py | Utility functions for indexing and environment loading |
| indexer/config.py | Configuration loading and saving for indexer settings |
| indexer/mcp_server.py |  |
| indexer/ruby_parser.py | Parses Ruby source files into structured symbol data |
| indexer/rust_parser.py | Parses Rust source files into structured symbol data |
| indexer/cli.py | Command-line interface for code indexing and search |
| indexer/task_store.py | Manages indexing tasks in a persistent store |
| indexer/hooks.py |  |
| indexer/cache.py | Sharded disk cache for parsed AST nodes |
| indexer/wiki.py | Generates wiki documentation pages and index |
| indexer/indexing.py | AST signature computation and cached description management for indexing |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/grouper.py::density_group` | function |  |
| `indexer/grouper.py::folder_of` | function |  |
| `indexer/grouper.py::prefixes` | function |  |
| `indexer/grouper.py::resolve_group` | function |  |
| `indexer/hooks.py::_hook_command` | function |  |
| `indexer/hooks.py::_hook_script_fresh` | function |  |
| `indexer/hooks.py::_hook_script_append` | function |  |
| `indexer/hooks.py::install_hook` | function |  |
| `indexer/hooks.py::remove_hook` | function |  |
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
| `indexer/ast_parser.py::ASTNode` | class | Represents a parsed AST node with metadata type docstring and calls |
| `indexer/ast_parser.py::_extract_imports` | function | Extracts import statements from the Python AST tree using walk |
| `indexer/ast_parser.py::_extract_calls` | function | Extracts function call names from the Python AST tree |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Identifies method IDs within a class definition from AST |
| `indexer/ast_parser.py::parse_file` | function | Parses a source file by language into ASTNode list using tree-sitter |
| `indexer/ast_parser.py::compute_hash_short` | function | Computes a short SHA256 hash of file contents for caching |
| `indexer/ast_parser.py::load_cached_nodes` | function | Loads cached parsed nodes from a JSON file on disk |
| `indexer/ast_parser.py::save_cached_nodes` | function | Saves parsed nodes to a JSON cache file using atomic write |
| `indexer/cache.py::_get_shard_lock` | function | Returns a threading Lock for a shard key to synchronize cache access |
| `indexer/cache.py::_atomic_write_json` | function | Atomically writes JSON data to a file using temporary file and replace |
| `indexer/cache.py::ShardedCache` | class | Manages a sharded on-disk cache for parsed AST nodes |
| `indexer/cache.py::ShardedCache.__init__` | method | Initializes the ShardedCache with root directory and max shard size |
| `indexer/cache.py::ShardedCache._dir` | method | Ensures the shard directory exists creating it if needed |
| `indexer/cache.py::ShardedCache._legacy_path` | method | Returns the legacy single-file cache path from cache config |
| `indexer/cache.py::ShardedCache.load` | method | Loads all cache shards from disk into a single dictionary |
| `indexer/cache.py::ShardedCache.save` | method | Saves the in-memory cache to sharded JSON files atomically |
| `indexer/config.py::EmbeddingConfig` | class | Configuration dataclass for embedding model settings |
| `indexer/config.py::VectorStoreConfig` | class | Configuration dataclass for vector store backend settings |
| `indexer/config.py::Config` | class | Top-level configuration dataclass containing all sub-configs |
| `indexer/config.py::_env` | function | Reads an environment variable with optional default |
| `indexer/config.py::_apply_env_field` | function | Sets a configuration field from environment variable if present |
| `indexer/config.py::_env_int` | function | Reads an environment variable and returns its integer value |
| `indexer/config.py::load_config` | function | Loads configuration from .indexer.toml and environment variable overrides |
| `indexer/config.py::_apply_env` | function | Applies all environment variable overrides to the configuration object |
| `indexer/config.py::save_config` | function | Saves the configuration dictionary to a TOML file atomically |
| `indexer/embedding.py::_get_openai_client` | function | Creates an OpenAI client instance using API key from environment |
| `indexer/embedding.py::_resolve_api_key` | function | Resolves the OpenAI API key from environment or .env file |
| `indexer/embedding.py::build_embedding_text` | function | Builds a text string from node fields for embedding computation |
| `indexer/embedding.py::compute_embedding_sig` | function | Computes a SHA256 signature of the embedding text for deduplication |
| `indexer/embedding.py::embed_nodes` | function | Computes embeddings for multiple AST nodes in parallel using threads |
| `indexer/embedding.py::embed_query` | function | Computes embedding vector for a text query string |
| `indexer/embedding.py::_call_embedding_api` | function | Calls the OpenAI embedding API with retries and rate limiting |
| `indexer/cli.py::main` | function | Defines CLI command group for the indexer tool |
| `indexer/cli.py::init` | function | Creates config installs pre-commit hook and appends to CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes the codebase computes embeddings and writes wiki pages |
| `indexer/cli.py::status` | function | Displays index status last commit stale files and manifest statistics |
| `indexer/cli.py::hook` | function | Groups subcommands for managing the pre-commit hook |
| `indexer/cli.py::hook_install` | function | Installs the pre-commit hook to run indexing on staged files |
| `indexer/cli.py::hook_remove` | function | Removes the pre-commit hook from the repository |
| `indexer/cli.py::serve` | function | Starts an MCP server for semantic code search and wiki retrieval |
| `indexer/cli.py::serve_api` | function | Starts a Flask REST API server for multi-repo semantic search |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures the cache directory is added to .gitignore file |
| `indexer/cli.py::_is_indexable` | function | Checks if a file path matches indexable extensions and not ignored |
| `indexer/cli.py::_parse_progress` | function | Parses and prints progress messages from indexing output |
| `indexer/git.py::_run` | function | Runs a git command and returns stdout warns on failure |
| `indexer/git.py::_run_checked` | function | Runs a git command raises GitOperationError on non-zero exit |
| `indexer/git.py::current_commit` | function | Returns the SHA of the current HEAD commit |
| `indexer/git.py::current_branch` | function | Returns the current git branch name or HEAD if detached |
| `indexer/git.py::staged_files` | function | Returns a list of staged file paths from git diff --cached |
| `indexer/git.py::changed_files_since` | function | Returns changed file paths since a given commit hash |
| `indexer/git.py::all_tracked_files` | function | Returns all git-tracked file paths in the repository |
| `indexer/git.py::is_git_repo` | function | Returns True if the current directory is a git repository |
| `indexer/go_parser.py::_get_go_language` | function | Returns a tree-sitter Language object for Go language |
| `indexer/go_parser.py::_extract_go_doc` | function | Extracts GoDoc comments from a tree-sitter node preceding comments |
| `indexer/go_parser.py::_extract_imports` | function | Extracts import paths from a Go AST using tree-sitter |
| `indexer/go_parser.py::_extract_calls` | function | Extracts function call identifiers from a Go AST |
| `indexer/go_parser.py::_get_receiver` | function | Extracts the receiver type name from a Go method declaration |
| `indexer/go_parser.py::_get_name` | function | Extracts the name identifier from a tree-sitter node |
| `indexer/go_parser.py::parse_go_file` | function | Parses a Go source file into ASTNode list using tree-sitter |
| `indexer/go_parser.py::visit` | function | Recursively visits Go AST nodes to build ASTNode list |
| `indexer/go_parser.py::visit` | function | Recursively visits Go AST nodes to build ASTNode list |
| `indexer/go_parser.py::visit` | function | Recursively visits Go AST nodes to build ASTNode list |
| `indexer/java_parser.py::_get_java_language` | function | Returns a tree-sitter Language object for Java |
| `indexer/java_parser.py::_extract_javadoc` | function | Extracts Javadoc comment text from a tree-sitter node |
| `indexer/java_parser.py::_extract_imports` | function | Extracts import statements from a Java AST using tree-sitter |
| `indexer/java_parser.py::_extract_calls` | function | Extracts method call identifiers from a Java AST |
| `indexer/java_parser.py::_get_name` | function | Extracts the name identifier from a Java tree-sitter node |
| `indexer/java_parser.py::_get_type_name` | function | Extracts the type name from a tree-sitter node |
| `indexer/java_parser.py::parse_java_file` | function | Parses a Java source file into ASTNode list using tree-sitter |
| `indexer/java_parser.py::visit` | function | Recursively visits Java AST nodes to extract name, javadoc, and called functions |
| `indexer/java_parser.py::visit` | function | Recursively visits Java AST nodes to extract name, javadoc, and called functions |
| `indexer/java_parser.py::visit` | function | Recursively visits Java AST nodes to extract name, javadoc, and called functions |
| `indexer/git_ops.py::GitOperationError` | class | Custom exception class for Git operation failures |
| `indexer/git_ops.py::GitOperationError.__init__` | method | Initializes GitOperationError with message via parent Exception |
| `indexer/git_ops.py::git_fetch_checkout_pull` | function | Fetches remote, checks out default branch, and pulls latest changes |
| `indexer/git_ops.py::_detect_default_branch` | function | Detects default branch by running git remote show and parsing output |
| `indexer/git_ops.py::_match_branch_rule` | function | Matches branch name against fnmatch patterns for include/exclude rules |
| `indexer/git_ops.py::_discover_remote_branches` | function | Discovers remote branches via git ls-remote, filtered by _match_branch_rule |
| `indexer/git_ops.py::_inject_credentials` | function | Embeds username/password into Git remote URL for authenticated access |
| `indexer/git_ops.py::_sanitize_error` | function | Sanitizes Git error output by stripping credentials and sensitive paths |
| `indexer/git_ops.py::_store_credentials` | function | Writes credential URL to a temporary file with restricted permissions for git use |
| `indexer/git_ops.py::_err` | function | Raises GitOperationError after sanitizing the error message |
| `indexer/js_parser.py::_get_language` | function | Selects tree-sitter language for JavaScript or TypeScript based on file extension |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts JSDoc comment text from a tree-sitter node, cleaning formatting |
| `indexer/js_parser.py::_extract_imports` | function | Extracts import specifiers from a tree-sitter AST by visiting import nodes |
| `indexer/js_parser.py::_extract_calls` | function | Recursively collects all function call names from a tree-sitter node |
| `indexer/js_parser.py::_get_name` | function | Retrieves the identifier name from a tree-sitter declaration node |
| `indexer/js_parser.py::parse_js_file` | function | Parses a JavaScript/TypeScript file into AST node list with name, doc, and calls |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
| `indexer/indexing.py::compute_ast_sig` | function | Computes a SHA-256 signature for the AST structure of a file |
| `indexer/indexing.py::_first_char_shard` | function | Returns the lowercased first character for sharding storage |
| `indexer/indexing.py::load_cached_descriptions` | function | Loads previously cached node descriptions from disk |
| `indexer/indexing.py::save_cached_descriptions` | function | Saves node descriptions dictionary to cache, filtering by IDs |
| `indexer/indexing.py::load_cached_file_descriptions` | function | Loads previously cached file descriptions from disk |
| `indexer/indexing.py::save_cached_file_descriptions` | function | Saves file descriptions dictionary to cache, filtering by file IDs |
| `indexer/indexing.py::prepare_descriptions` | function | Generates LLM descriptions for nodes and files in parallel batches with caching |
| `indexer/indexing.py::cross_reference` | function | Builds a reverse mapping from called functions to their defining nodes |
| `indexer/indexing.py::load_existing_nodes` | function | Loads previously parsed and cached nodes for unchanged files in parallel |
| `indexer/indexing.py::parse_candidates` | function | Parses files identified as candidates into AST nodes using parallel workers |
| `indexer/indexing.py::build_batches` | function | Splits a list of items into fixed-size batches for LLM processing |
| `indexer/indexing.py::_collect_affected_files` | function | Collects file paths that are referenced by or declare changed symbols |
| `indexer/indexing.py::write_wiki_pages` | function | Generates and writes Markdown wiki pages for each indexed code symbol |
| `indexer/indexing.py::write_index_and_skill` | function | Generates index.json and skill.yaml from parsed nodes and manifest |
| `indexer/indexing.py::update_manifest` | function | Updates the project manifest with current file hashes and timestamps |
| `indexer/indexing.py::load_cached_embeddings` | function | Loads previously cached embedding vectors from disk |
| `indexer/indexing.py::save_cached_embeddings` | function | Saves embedding vectors to cache for later reuse |
| `indexer/indexing.py::upsert_vectors` | function | Upserts node and file embeddings into the vector index, deleting stale entries |
| `indexer/indexing.py::_load_one` | function | Loads a single cached node file if its hash matches and file exists |
| `indexer/llm.py::_EmptyResponseError` | class | Exception raised when the LLM returns an empty response |
| `indexer/llm.py::_is_anthropic` | function | Returns True if the model string matches Anthropic providers |
| `indexer/llm.py::_resolve_api_key` | function | Resolves the API key for the current LLM provider from environment or config |
| `indexer/llm.py::_litellm_kwargs` | function | Builds keyword arguments dictionary for LiteLLM completion call |
| `indexer/llm.py::_litellm_completion` | function | Calls LiteLLM completion with exponential backoff retry on failure |
| `indexer/llm.py::_get_anthropic_client` | function | Creates an instance of the Anthropic API client from environment |
| `indexer/llm.py::_anthropic_completion` | function | Calls Anthropic API directly with retry and backoff for completion |
| `indexer/llm.py::_should_use_anthropic_sdk` | function | Returns True if the model should use the direct Anthropic SDK instead of LiteLLM |
| `indexer/llm.py::_parse_llm_json` | function | Parses LLM JSON response with recovery for truncation and malformed output |
| `indexer/llm.py::describe_nodes_batch` | function | Sends a batch of nodes to the LLM for description generation in one call |
| `indexer/llm.py::describe_nodes` | function | Generates descriptions for all nodes via parallel batched LLM calls |
| `indexer/llm.py::describe_files` | function | Generates file-level descriptions via parallel batched LLM calls |
| `indexer/llm.py::_describe_files_chunk` | function | Sends a chunk of file summaries to the LLM for description generation |
| `indexer/llm.py::deep_enrich_page` | function | Calls LLM to enrich one wiki page with deeper synthesis and explanations |
| `indexer/llm.py::deep_enrich_pages` | function | Enriches multiple wiki pages in parallel using batched LLM calls |
| `indexer/llm.py::deep_enrich_index` | function | Calls LLM to generate an enriched index page with overview and cross-references |
| `indexer/llm.py::rewrite_query` | function | Rewrites the user natural language query into a structured search query |
| `indexer/llm.py::synthesize_commit_message` | function | Synthesizes a commit message from the diff using LLM |
| `indexer/manifest.py::FileEntry` | class | Data class holding file path and hash for manifest entries |
| `indexer/manifest.py::Manifest` | class | Manages the project manifest: loading, saving, and checking file staleness |
| `indexer/manifest.py::Manifest.stale_files` | method | Returns list of files whose hash has changed since last manifest save |
| `indexer/manifest.py::Manifest.removed_files` | method | Returns list of files that were in previous manifest but no longer exist |
| `indexer/manifest.py::compute_hash` | function | Computes SHA-256 hex digest of a file binary contents |
| `indexer/manifest.py::load_manifest` | function | Reads and parses the manifest JSON file into a Manifest object |
| `indexer/manifest.py::save_manifest` | function | Atomically writes the manifest dictionary to a JSON file |
| `indexer/manifest.py::_check` | function | Compares current file hash with stored hash; returns True if changed |
| `indexer/repo_registry.py::_get_repo_lock` | function | Returns or creates a threading Lock for a specific repository name |
| `indexer/repo_registry.py::RepoRegistry` | class | Thread-safe registry for repository metadata and configuration |
| `indexer/repo_registry.py::RepoRegistry.__init__` | method | Initializes RepoRegistry with a temporary directory and a reentrant lock |
| `indexer/repo_registry.py::RepoRegistry._save` | method | Atomically writes the internal registry dictionary to a JSON file |
| `indexer/repo_registry.py::RepoRegistry._load` | method | Loads registry from disk, detecting default branch and migrating old format |
| `indexer/repo_registry.py::RepoRegistry.register` | method | Registers a repository by saving its config and updating remote branches |
| `indexer/repo_registry.py::RepoRegistry.unregister` | method | Unregisters a repository, evicts its client, and removes config |
| `indexer/repo_registry.py::RepoRegistry.get` | method | Returns a deep copy of the repository configuration by name |
| `indexer/repo_registry.py::RepoRegistry.list_names` | method | Returns sorted list of all registered repository names |
| `indexer/repo_registry.py::RepoRegistry.items` | method | Returns list of (repo name, config) tuples for all registered repos |
| `indexer/repo_registry.py::RepoRegistry.update_meta` | method | Updates repository metadata fields after validating the repo exists |
| `indexer/rest_api.py::register_repo` | function | Handles POST /repos to register a new repository with branch discovery |
| `indexer/rest_api.py::task_status` | function | Returns the status of a background task in JSON format |
| `indexer/rest_api.py::validate_repo` | function | Validates repository index integrity: checks files, manifest, and wiki paths |
| `indexer/rest_api.py::sync_repo` | function | Creates sync task and runs it in executor |
| `indexer/rest_api.py::rebuild_repo` | function | Creates rebuild task and runs it in executor |
| `indexer/rest_api.py::_run_all_branches` | function | Acquires lock and runs function on all branches |
| `indexer/rest_api.py::sync_all_branches` | function | Discovers branches and runs sync tasks for each |
| `indexer/rest_api.py::reindex_repo` | function | Atomically updates meta, rediscover branches, rebuild all |
| `indexer/rest_api.py::rebuild_all_branches` | function | Discovers branches and runs rebuild tasks for each |
| `indexer/rest_api.py::_run_indexing_pipeline` | function | Collects affected files, densifies, enriches, writes indexes and vectors |
| `indexer/rest_api.py::_run_rebuild_task` | function | Acquires lock, runs inner rebuild, releases lock |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function | Clones/fetches repo, installs webhook, runs indexing pipeline |
| `indexer/rest_api.py::_run_sync_task` | function | Fetches branch, computes diff, updates index and wiki |
| `indexer/rest_api.py::_run_register_task` | function | Acquires lock, runs inner register, releases lock |
| `indexer/rest_api.py::_run_register_task_inner` | function | Clones repo, installs webhook, stores credentials, indexes all branches |
| `indexer/rest_api.py::unregister_repo` | function | Unregisters repo by name, returns success JSON |
| `indexer/rest_api.py::search_symbols` | function | Parses body, embeds query, reranks symbols, returns results |
| `indexer/rest_api.py::trace_call` | function | Resolves repos, calls trace impl, returns call graph JSON |
| `indexer/rest_api.py::get_source_context` | function | Reads source file, extracts lines around symbol position |
| `indexer/rest_api.py::list_repos` | function | Aggregates repo metadata and returns JSON list |
| `indexer/rest_api.py::health` | function | Checks if any repos exist and returns JSON |
| `indexer/rest_api.py::repo_detail` | function | Returns detailed repo stats, collections, wiki pages |
| `indexer/rest_api.py::wiki_page_content` | function | Reads wiki page file and returns content |
| `indexer/rest_api.py::update_repo_meta` | function | Updates repo metadata from request body |
| `indexer/rest_api.py::multi_repo_skill` | function | Aggregates skills from all repos into combined JSON |
| `indexer/rest_api.py::_get_webhook_url` | function | Constructs webhook URL with HMAC signature |
| `indexer/rest_api.py::_webhook_sign` | function | Generates HMAC-SHA256 signature for payload |
| `indexer/rest_api.py::_verify_webhook_sign` | function | Compares provided signature with computed HMAC |
| `indexer/rest_api.py::webhook_by_name` | function | Handles Git webhook: verifies signature, triggers sync |
| `indexer/rest_api.py::create_app` | function | Creates Starlette app with routes, middleware, static files |
| `indexer/rest_api.py::_index_page` | function | Serves static index.html if exists, else 404 JSON |
| `indexer/rest_api.py::_resolve_repos` | function | Resolves repo IDs from query or body parameters |
| `indexer/rest_api.py::_trace_call_impl` | function | Delegates to retrieval trace call with expanded graph |
| `indexer/rest_api.py::_expand_with_call_graph` | function | Expands symbol list using call graph retrieval |
| `indexer/rest_api.py::_InvalidBodyError` | class | Exception for invalid request body JSON |
| `indexer/rest_api.py::_parse_body` | function | Parses JSON body, raises _InvalidBodyError on failure |
| `indexer/rest_api.py::_run_all` | function | Acquires lock, runs rebuild inner, releases lock |
| `indexer/rest_api.py::_LoggingMiddleware` | class | ASGI middleware that logs request duration |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method | Logs request processing time, calls next middleware |
| `indexer/rest_api.py::_invalid_body_handler` | function | Returns 400 JSON response for invalid body errors |
| `indexer/rest_api.py::_AuthMiddleware` | class | ASGI middleware that validates Bearer token |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method | Checks token, returns 401 if invalid, else passes |
| `indexer/rust_parser.py::_get_rust_language` | function | Initializes tree-sitter Rust language object |
| `indexer/rust_parser.py::_extract_rust_doc` | function | Extracts Rust doc comments from node text |
| `indexer/rust_parser.py::_extract_imports` | function | Collects import paths from Rust source node children |
| `indexer/rust_parser.py::_extract_calls` | function | Collects function call identifiers from node |
| `indexer/rust_parser.py::_get_name` | function | Returns name from node's name child |
| `indexer/rust_parser.py::parse_rust_file` | function | Parses Rust file into AST nodes with metadata |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/retrieval.py::truncate_documents` | function | Truncates document strings to given max length |
| `indexer/retrieval.py::search_symbols` | function | Embeds query, expands call graph, reranks and returns symbols |
| `indexer/retrieval.py::trace_call` | function | Recursively fetches callers/callees to build call chain |
| `indexer/retrieval.py::get_source_context` | function | Reads source file and extracts lines with context |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Recursively expands symbol set with callers and callees |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON string into Python list |
| `indexer/ruby_parser.py::_get_ruby_language` | function | Initializes tree-sitter Ruby language object |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function | Extracts Ruby comments from node text |
| `indexer/ruby_parser.py::_extract_imports` | function | Collects require/include paths from Ruby node |
| `indexer/ruby_parser.py::_extract_calls` | function | Collects method call identifiers from Ruby node |
| `indexer/ruby_parser.py::_get_name` | function | Returns name from Ruby node's name child |
| `indexer/ruby_parser.py::parse_ruby_file` | function | Parses Ruby file into AST nodes with metadata |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/task_store.py::TaskStore` | class | In-memory task storage with TTL-based cleanup |
| `indexer/task_store.py::TaskStore.__init__` | method | Initializes empty tasks dict and threading Lock |
| `indexer/task_store.py::TaskStore._cleanup` | method | Removes tasks older than TTL from store |
| `indexer/task_store.py::TaskStore.create` | method | Creates new task with UUID and current timestamp |
| `indexer/task_store.py::TaskStore.get` | method | Returns deep copy of task by ID |
| `indexer/task_store.py::TaskStore.update` | method | Updates task status and sets current timestamp |
| `indexer/wiki.py::PageContext` | class | Data class holding page name, title, and content |
| `indexer/wiki.py::IndexEntry` | class | Data class holding entry name, path, and signature |
| `indexer/wiki.py::_jinja_env` | function | Returns shared Jinja2 environment for templates |
| `indexer/wiki.py::build_page` | function | Renders wiki page from template and context |
| `indexer/wiki.py::build_index` | function | Renders wiki index page using Jinja template |
| `indexer/wiki.py::sanitize_group_label` | function | Replaces invalid characters in group label |
| `indexer/wiki.py::resolve_wiki_page_path` | function | Resolves wiki page file path from group label |
| `indexer/wiki.py::_atomic_write_text` | function | Writes text atomically via temporary file and rename |
| `indexer/wiki.py::write_page` | function | Creates directories and writes wiki page file |
| `indexer/wiki.py::write_index` | function | Creates directory and atomically writes index text |
| `indexer/utils.py::resolve_api_key` | function | Retrieves API key and replaces characters, checks uppercase |
| `indexer/utils.py::_rel` | function | Converts path to relative string using relative_to |
| `indexer/utils.py::_node_text` | function | Decodes node text from bytes to string |
| `indexer/utils.py::load_env_file` | function | Reads .env file and returns dict of key-value pairs |
| `indexer/vector_store.py::_get_client` | function | Returns PersistentClient, creating or reusing from pool |
| `indexer/vector_store.py::evict_client` | function | Removes and closes a Chroma client from pool |
| `indexer/vector_store.py::_get_or_create_collection` | function | Gets or creates Chroma collection, validates dimension consistency |
| `indexer/vector_store.py::upsert_nodes` | function | Upserts nodes into Chroma, builds embeddings and metadata |
| `indexer/vector_store.py::search` | function | Queries Chroma collection with text, returns matches list |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves documents by IDs from Chroma collection |
| `indexer/vector_store.py::delete_by_files` | function | Deletes documents belonging to given file paths from Chroma |
| `indexer/vector_store.py::_build_doc` | function | Concatenates node fields into a single document string |
| `indexer/vector_store.py::_truncate_list` | function | Truncates list to fit token budget, logs warning if truncated |
| `indexer/vector_store.py::_build_meta` | function | Builds metadata dict, truncates large lists for Chroma |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes object to compact JSON without whitespace |
## Data Flows
- CLI init → indexing.py walks repo → per-language parse_file → ASTNode list → embedding.py → vector_store upsert → retrieval ready
- MCP client calls search_symbols_tool → retrieval.py queries vector_store → returns ranked symbol matches with source context (get_source_context_tool)
- Developer runs git commit → install_hook triggers pre-commit → hooks.py runs _hook_command → incremental re-index of changed files via cache.py and task_store.py
- User invokes grouper.density_group on symbol results → resolve_group computes folder_of and prefixes → clusters symbols by path prefix density for AI-focused output
## Design Constraints
- ASTNode.calls are extracted via static AST walk (walk); dynamic or indirect calls (e.g., via getattr) are NOT captured, leading to incomplete traces.
- grouper.density_group groups files by prefix density, not directory hierarchy; a file at a/b/c/d.py may be grouped with a/b/x/d.py if density of 'a/b/' is low, but not with a/e.py if 'a/' density is high.
- MCP server authentication uses _MCPAuthMiddleware which compares tokens with compare_digest; only a single static API token is supported (no multi-user or scoped tokens).
- Hooks (install_hook, remove_hook) modify .git/hooks directly as shell scripts; they assume a Unix-like environment and will fail on Windows without WSL.
- The ast_parser uses tree-sitter for non-Python languages (Ruby, Rust, Java, Go, JS) but falls back to Python's ast module for .py files; parsing failures on malformed code silently return empty ASTNode instead of raising.
- Vector store operations (vector_store.py) are not transactional; concurrent indexing jobs may produce partial or duplicated vectors if not locked externally.
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, FastMCP, FileEntry, GitOperationError, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Parser, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, __init__, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _atomic_write_json, _atomic_write_text, _build_doc, _build_meta, _call_embedding_api, _cleanup, _collect_affected_files, _desc_cache, _detect_default_branch, _discover_remote_branches, _emb_cache, _ensure_cache_gitignore, _env, _env_int, _err, _expand_retrieval, _expand_with_call_graph, _extract_calls, _extract_go_doc, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _extract_rust_doc, _fdesc_cache, _get_anthropic_client, _get_class_method_ids, _get_client, _get_go_language, _get_java_language, _get_language, _get_name, _get_openai_client, _get_or_create_collection, _get_receiver, _get_repo_lock, _get_ruby_language, _get_rust_language, _get_shard_lock, _get_webhook_url, _hook_command, _hook_script_append, _hook_script_fresh, _inject_credentials, _is_anthropic, _is_indexable, _jinja_env, _litellm_completion, _litellm_kwargs, _load_one, _match_branch_rule, _node_text, _orig_method, _parse_body, _parse_json_list, _parse_llm_json, _rel, _resolve_api_key, _resolve_repos, _run, _run_all_branches, _run_checked, _run_indexing_pipeline, _run_rebuild_task_inner, _run_register_task_inner, _sanitize_error, _save, _shard_fn, _should_use_anthropic_sdk, _store_credentials, _trace_call_impl, _trace_call_retrieval, _truncate_list, _verify_webhook_sign, _webhook_sign, acquire, add, all, all_tracked_files, any, append, as_completed, asdict, body, bool, build_batches, build_embedding_text, build_index, build_page, call_next, changed_files_since, child_by_field_name, chmod, command, compare_digest, completion, compute_ast_sig, compute_embedding_sig, compute_hash, compute_hash_short, count, create, create_api_server, create_app, create_server, cross_reference, current_branch, current_commit, cwd, debug, decode, deep_enrich_index, deep_enrich_pages, deepcopy, defaultdict, delete, density_group, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, fnmatch, folder_of, fromkeys, get, get_by_ids, get_collection, get_docstring, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, git_fetch_checkout_pull, glob, group, hasattr, hexdigest, id, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_names, load, load_cached_descriptions, load_cached_embeddings, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, pop, prefixes, prepare_descriptions, progress_callback, query, quote, range, read, read_bytes, read_text, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_api_key, resolve_group, resolve_wiki_page_path, result, rewrite_query, rfind, rglob, rmtree, rsplit, rstrip, run, run_fn, run_in_executor, sanitize_fn, sanitize_group_label, save, save_cached_descriptions, save_cached_embeddings, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha256, sleep, sort, sorted, split, splitlines, staged_files, stale_files, startswith, stat, str, strftime, strip, sub, submit, sum, super, synthesize_commit_message, time, tool, trace_call, truncate_documents, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, with_suffix, write, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/ast_parser.py::save_cached_nodes, indexer/cache.py::ShardedCache.save, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::compute_embedding_sig, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::_run_checked, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_err, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/indexing.py::_load_one, indexer/indexing.py::load_existing_nodes, indexer/indexing.py::parse_candidates, indexer/indexing.py::prepare_descriptions, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/indexing.py::write_wiki_pages, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_anthropic_completion, indexer/llm.py::_describe_files_chunk, indexer/llm.py::_litellm_completion, indexer/llm.py::_resolve_api_key, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::_check, indexer/manifest.py::load_manifest, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::trace_call_tool, indexer/repo_registry.py::RepoRegistry._load, indexer/repo_registry.py::RepoRegistry.register, indexer/repo_registry.py::RepoRegistry.unregister, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all, indexer/rest_api.py::_run_all_branches, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::get_source_context, indexer/rest_api.py::list_repos, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::search_symbols, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::resolve_wiki_page_path, indexer/wiki.py::write_index, indexer/wiki.py::write_page, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default, tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic, tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty, tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, copy, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cache.ShardedCache, indexer.cache._atomic_write_json, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git._GIT_ENV, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.git_ops.GitOperationError, indexer.git_ops._detect_default_branch, indexer.git_ops._discover_remote_branches, indexer.git_ops._inject_credentials, indexer.git_ops._match_branch_rule, indexer.git_ops._sanitize_error, indexer.git_ops._store_credentials, indexer.git_ops.git_fetch_checkout_pull, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing._collect_affected_files, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.prepare_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.repo_registry.RepoRegistry, indexer.repo_registry._get_repo_lock, indexer.repo_registry._locks_lock, indexer.repo_registry._repo_locks, indexer.rest_api.create_app, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.get_source_context, indexer.retrieval.search_symbols, indexer.retrieval.trace_call, indexer.retrieval.truncate_documents, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.task_store.TaskStore, indexer.utils.FATAL_EXCEPTIONS, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.utils.resolve_api_key, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki._atomic_write_text, indexer.wiki._jinja_env, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.resolve_wiki_page_path, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_go, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_rust, tree_sitter_typescript, typing.Callable, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
## Entry Points
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `ShardedCache`
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
- `wiki_page_content`
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
- `upsert_nodes`
- `delete_by_files`
