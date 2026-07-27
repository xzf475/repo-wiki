# indexer/

## Overview

The indexer module provides a persistent, cross-language code index that enables AI agents to perform semantic search, retrieve edit context, and generate change plans. It parses source files into ASTNode objects via language-specific parsers (Python, Ruby, JS, Go, Java, Rust), computes embeddings for vector search, and stores results in a Vectra-based vector store with disk caching. The system tracks git history to detect stale files, uses a manifest to track indexed state, and exposes functionality via CLI, MCP server, and REST API. Key classes include ASTNode (unified AST representation), RepoRegistry (multi-repo management), VectorStore (embedding storage), and EmbeddingConfig (model settings). The module also provides agent-specific tools like post-edit verification and index diagnostics.

## Modules
| File | Purpose |
|------|---------|
| indexer/embedding.py | Generates and caches embeddings for AST nodes |
| indexer/git.py | Git repository querying and file tracking utilities |
| indexer/wiki.py | Generates wiki documentation pages and index |
| indexer/repo_registry.py | Registry for managing repository locks and state |
| indexer/grouper.py |  |
| indexer/ast_parser.py | AST parser for extracting code structure and dependencies |
| indexer/ruby_parser.py | Parses Ruby source files into structured symbol data |
| indexer/mcp_server.py | MCP server exposing code search and analysis tools |
| indexer/cli.py | CLI entry point for indexing and agent workflows |
| indexer/js_parser.py | Tree-sitter based parser for JavaScript source code analysis |
| indexer/agent_diff.py | Verifies post-edit diffs and generates change reports |
| indexer/task_store.py | Manages indexing tasks in a persistent store |
| indexer/retrieval.py | Core retrieval and impact analysis for code symbols |
| indexer/go_parser.py | Tree-sitter based parser for Go source code analysis |
| indexer/config.py | Configuration loading and saving for indexer settings |
| indexer/rest_api.py | REST API endpoints for repository registration, syncing, and rebuilding |
| indexer/cache.py | Sharded disk cache for parsed AST nodes |
| indexer/git_ops.py | Git operations for repository fetching and checkout |
| indexer/utils.py | Utility functions for indexing and environment loading |
| indexer/agent_graph.py | Agent cross-repo dependency graph builder |
| indexer/hooks.py |  |
| indexer/indexing.py | AST signature computation and cached description management for indexing |
| indexer/vector_store.py | Vector store abstraction for code embeddings and search |
| indexer/agent_contracts.py | Defines agent capabilities manifest and schemas |
| indexer/manifest.py | Manifest management with hashing and persistence for file tracking |
| indexer/java_parser.py | Tree-sitter based parser for Java source code analysis |
| indexer/agent_context.py | Resolves symbols and plans changes for agent context |
| indexer/rust_parser.py | Parses Rust source files into structured symbol data |
| indexer/llm.py | LLM client abstraction for generating node and file descriptions |
| indexer/agent_diagnostics.py | Diagnoses index issues for agent |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class | Data class representing an AST node with id, type, location, docstring, and calls. |
| `indexer/ast_parser.py::_extract_imports` | function | Extracts import statements from an AST by walking and checking node types. |
| `indexer/ast_parser.py::_extract_calls` | function | Extracts function call names from an AST by walking and collecting Call nodes. |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Gets method IDs from class AST nodes by walking and finding FunctionDef nodes. |
| `indexer/ast_parser.py::_entry_point_from_decorators` | function | Infers entry point kind from decorators like @app.route. |
| `indexer/ast_parser.py::parse_file` | function | Parses a source file into ASTNode objects using language-specific parsers and calls extraction. |
| `indexer/ast_parser.py::compute_hash_short` | function | Computes a short SHA256 hash of file bytes for change detection. |
| `indexer/ast_parser.py::load_cached_nodes` | function | Loads previously cached AST nodes from a JSON file. |
| `indexer/ast_parser.py::save_cached_nodes` | function | Saves AST nodes to a cache JSON file using atomic write. |
| `indexer/cli.py::main` | function | Entry point for CLI, registers subcommand groups. |
| `indexer/cli.py::init` | function | Initializes .indexer.toml, installs pre-commit hook, and appends to CLAUDE.md. |
| `indexer/cli.py::run` | function | Indexes the codebase and generates wiki pages with cross-references. |
| `indexer/cli.py::status` | function | Shows last indexed commit, stale files, and manifest statistics. |
| `indexer/cli.py::agent` | function | Groups agent code-location subcommands. |
| `indexer/cli.py::agent_context` | function | Prints edit-context bundle for a symbol via get_edit_context. |
| `indexer/cli.py::agent_verify` | function | Suggests verification commands after an Agent edit via post_edit_verify. |
| `indexer/cli.py::agent_plan` | function | Prints Agent change plan using change_plan function. |
| `indexer/cli.py::agent_diagnose` | function | Prints local index health diagnostics via diagnose_index. |
| `indexer/cli.py::agent_capabilities` | function | Prints the Agent tool manifest via agent_capabilities_manifest. |
| `indexer/cli.py::agent_schema` | function | Prints the machine-readable Agent API schema via agent_schema. |
| `indexer/cli.py::hook` | function | Groups pre-commit hook management subcommands. |
| `indexer/cli.py::hook_install` | function | Installs the pre-commit hook in the current repository. |
| `indexer/cli.py::hook_remove` | function | Removes the pre-commit hook from the current repository. |
| `indexer/cli.py::serve` | function | Starts the MCP server for semantic code search using create_server. |
| `indexer/cli.py::serve_api` | function | Starts REST API server for remote semantic code search across multiple repos. |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures .gitignore includes the index cache directory. |
| `indexer/cli.py::_is_indexable` | function | Checks if a file path matches indexable patterns using fnmatch. |
| `indexer/cli.py::_json_dumps` | function | Dumps a value as pretty-printed JSON string. |
| `indexer/cli.py::_parse_progress` | function | Parses and echoes progress messages from indexing. |
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
| `indexer/grouper.py::density_group` | function |  |
| `indexer/grouper.py::folder_of` | function |  |
| `indexer/grouper.py::prefixes` | function |  |
| `indexer/grouper.py::resolve_group` | function |  |
| `indexer/hooks.py::_hook_command` | function |  |
| `indexer/hooks.py::_hook_script_fresh` | function |  |
| `indexer/hooks.py::_hook_script_append` | function |  |
| `indexer/hooks.py::install_hook` | function |  |
| `indexer/hooks.py::remove_hook` | function |  |
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
| `indexer/js_parser.py::_get_language` | function | Selects tree-sitter language for JavaScript or TypeScript based on file extension |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts JSDoc comment text from a tree-sitter node, cleaning formatting |
| `indexer/js_parser.py::_extract_imports` | function | Extracts import specifiers from a tree-sitter AST by visiting import nodes |
| `indexer/js_parser.py::_extract_calls` | function | Recursively collects all function call names from a tree-sitter node |
| `indexer/js_parser.py::_get_name` | function | Retrieves the identifier name from a tree-sitter declaration node |
| `indexer/js_parser.py::parse_js_file` | function | Parses a JavaScript/TypeScript file into AST node list with name, doc, and calls |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
| `indexer/js_parser.py::visit` | function | Recursively walks JS AST nodes, extracting name, doc, and inner calls into ASTNode |
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
| `indexer/mcp_server.py::_apply_mcp_auth` | function | Applies MCP authentication middleware comparing API key from header. |
| `indexer/mcp_server.py::create_server` | function | Creates FastMCP server registering all code search and edit tools. |
| `indexer/mcp_server.py::create_api_server` | function | Creates FastMCP API server for remote multi-repo semantic code search. |
| `indexer/mcp_server.py::_patched_method` | function | Patches HTTP method with MCP authentication middleware. |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches code symbols semantically across one or all repos |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call chain for a symbol using API post |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code context around given line range |
| `indexer/mcp_server.py::get_edit_context_tool` | function | Returns edit-ready context bundle for a symbol |
| `indexer/mcp_server.py::resolve_symbol_tool` | function | Resolves query or symbol name to a component_id |
| `indexer/mcp_server.py::find_tests_for_symbol_tool` | function | Finds likely test files for a symbol in a repo |
| `indexer/mcp_server.py::pre_edit_check_tool` | function | Runs pre-edit checks for a symbol |
| `indexer/mcp_server.py::impact_analysis_tool` | function | Analyzes symbol change impact via callers, callees, tests, risks, freshness |
| `indexer/mcp_server.py::change_plan_tool` | function | Creates modification plan for a goal and target symbol |
| `indexer/mcp_server.py::diagnose_index_tool` | function | Diagnoses index integrity for manifest, wiki, vector DB, source, freshness |
| `indexer/mcp_server.py::agent_protocol_tool` | function | Returns compact agent protocol fields for editing and verification |
| `indexer/mcp_server.py::locate_from_error_tool` | function | Locates code symbols from error text, stack trace, or HTTP path |
| `indexer/mcp_server.py::list_entry_points_tool` | function | Lists indexed entry points for API, CLI, events, jobs, webhooks |
| `indexer/mcp_server.py::post_edit_verify_tool` | function | Verifies local edits before commit, using git diff if omitted |
| `indexer/mcp_server.py::change_set_tool` | function | Builds must-change set from a goal and target symbol or diff |
| `indexer/mcp_server.py::coverage_map_tool` | function | Maps source symbols to likely covering tests |
| `indexer/mcp_server.py::index_diff_report_tool` | function | Summarizes symbol and call graph changes between two snapshots |
| `indexer/mcp_server.py::cross_repo_graph_tool` | function | Returns empty cross-repo graph for local single-repo mode |
| `indexer/mcp_server.py::agent_capabilities_manifest_tool` | function | Returns tool capability manifest and recommended Agent flow |
| `indexer/mcp_server.py::stable_symbol_id_tool` | function | Generates deterministic stable symbol id for rename tracking |
| `indexer/mcp_server.py::get_index_status_tool` | function | Reports if local index is stale relative to workspace |
| `indexer/mcp_server.py::_api_request` | function | Sends HTTP request to indexer API, returns parsed response |
| `indexer/mcp_server.py::_api_get` | function | Performs HTTP GET request via _api_request |
| `indexer/mcp_server.py::_api_post` | function | Performs HTTP POST request via _api_request |
| `indexer/mcp_server.py::list_repos` | function | Lists all registered repositories with names, descriptions, tags, stats |
| `indexer/mcp_server.py::search_symbols_tool` | function | Searches code symbols semantically across one or all repos |
| `indexer/mcp_server.py::trace_call_tool` | function | Traces call chain for a symbol using API post |
| `indexer/mcp_server.py::get_source_context_tool` | function | Reads source code context around given line range |
| `indexer/mcp_server.py::get_edit_context_tool` | function | Returns edit-ready context bundle for a symbol |
| `indexer/mcp_server.py::resolve_symbol_tool` | function | Resolves query or symbol name to a component_id |
| `indexer/mcp_server.py::find_tests_for_symbol_tool` | function | Finds likely test files for a symbol in a repo |
| `indexer/mcp_server.py::pre_edit_check_tool` | function | Runs pre-edit checks for a symbol |
| `indexer/mcp_server.py::impact_analysis_tool` | function | Analyzes symbol change impact via callers, callees, tests, risks, freshness |
| `indexer/mcp_server.py::change_plan_tool` | function | Creates modification plan for a goal and target symbol |
| `indexer/mcp_server.py::diagnose_index_tool` | function | Diagnoses index integrity for manifest, wiki, vector DB, source, freshness |
| `indexer/mcp_server.py::agent_protocol_tool` | function | Returns compact agent protocol fields for editing and verification |
| `indexer/mcp_server.py::locate_from_error_tool` | function | Locates code symbols from error text, stack trace, or HTTP path |
| `indexer/mcp_server.py::list_entry_points_tool` | function | Lists indexed entry points for API, CLI, events, jobs, webhooks |
| `indexer/mcp_server.py::post_edit_verify_tool` | function | Verifies local edits before commit, using git diff if omitted |
| `indexer/mcp_server.py::change_set_tool` | function | Builds must-change set from a goal and target symbol or diff |
| `indexer/mcp_server.py::coverage_map_tool` | function | Maps source symbols to likely covering tests |
| `indexer/mcp_server.py::index_diff_report_tool` | function | Summarizes symbol and call graph changes between two snapshots |
| `indexer/mcp_server.py::cross_repo_graph_tool` | function | Returns empty cross-repo graph for local single-repo mode |
| `indexer/mcp_server.py::agent_capabilities_manifest_tool` | function | Returns tool capability manifest and recommended Agent flow |
| `indexer/mcp_server.py::stable_symbol_id_tool` | function | Generates deterministic stable symbol id for rename tracking |
| `indexer/mcp_server.py::get_index_status_tool` | function | Reports if local index is stale relative to workspace |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class | ASGI middleware that validates bearer token via digest comparison |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method | Dispatches request after validating bearer token |
| `indexer/retrieval.py::truncate_documents` | function | Truncates document list to max length |
| `indexer/retrieval.py::search_symbols` | function | Searches symbols by embedding query, expands call graph, annotates reasons |
| `indexer/retrieval.py::resolve_symbol` | function | Resolves symbol to component ID via _impl |
| `indexer/retrieval.py::impact_analysis` | function | Performs impact analysis via _impl |
| `indexer/retrieval.py::change_plan` | function | Creates modification plan via _impl |
| `indexer/retrieval.py::diagnose_index` | function | Diagnoses index integrity via _impl |
| `indexer/retrieval.py::agent_protocol_bundle` | function | Builds agent protocol bundle including change plan |
| `indexer/retrieval.py::list_entry_points` | function | Lists entry points via _impl |
| `indexer/retrieval.py::locate_from_error` | function | Locates symbols from error text via _impl |
| `indexer/retrieval.py::post_edit_verify` | function | Verifies edits before commit via _impl |
| `indexer/retrieval.py::stable_symbol_id` | function | Generates stable symbol ID via _impl |
| `indexer/retrieval.py::change_set` | function | Builds change set via _impl |
| `indexer/retrieval.py::coverage_map` | function | Maps symbols to tests via _impl |
| `indexer/retrieval.py::index_diff_report` | function | Reports index diff between snapshots via _impl |
| `indexer/retrieval.py::cross_repo_graph` | function | Builds cross-repo graph via _impl |
| `indexer/retrieval.py::agent_capabilities_manifest` | function | Returns agent capabilities manifest via _manifest |
| `indexer/retrieval.py::trace_call` | function | Traces call graph for a symbol, returns callees and callers |
| `indexer/retrieval.py::get_source_context` | function | Reads source code context for a file and line range |
| `indexer/retrieval.py::get_index_status` | function | Reports if index is stale by comparing tracked files and git state |
| `indexer/retrieval.py::find_tests_for_symbol` | function | Finds likely test files for a symbol by manifest and path patterns |
| `indexer/retrieval.py::get_edit_context` | function | Builds edit context with source, index status, and test files |
| `indexer/retrieval.py::pre_edit_check` | function | Runs pre-edit checks: dirty files, test commands, index status |
| `indexer/retrieval.py::recommend_test_commands` | function | Recommends test commands for a symbol based on file patterns |
| `indexer/retrieval.py::_git_dirty_files` | function | Returns list of dirty files from git status |
| `indexer/retrieval.py::_expand_with_call_graph` | function | Expands symbol list by traversing call graph up/down |
| `indexer/retrieval.py::_annotate_match_reasons` | function | Annotates search results with match reason scores |
| `indexer/retrieval.py::_natural_language_alias_score` | function | Scores symbol name alias against query for natural language matches |
| `indexer/retrieval.py::_looks_like_entry_point` | function | Checks if symbol metadata suggests it is an entry point |
| `indexer/retrieval.py::_freshness_risks` | function | Extracts freshness risk indicators from index status |
| `indexer/retrieval.py::_infer_entry_point_kind_from_hit` | function | Infers entry point kind from symbol hit metadata |
| `indexer/retrieval.py::_extract_error_frames` | function | Extracts stack trace frames from error text using regex |
| `indexer/retrieval.py::_extract_http_paths` | function | Extracts HTTP paths from error text using regex |
| `indexer/retrieval.py::_extract_error_terms` | function | Extracts lowercase error terms from text, filtering digits |
| `indexer/retrieval.py::_git_diff` | function | Returns git diff output for the repository |
| `indexer/retrieval.py::_parse_diff_changed_files` | function | Parses git diff output to extract changed file paths |
| `indexer/retrieval.py::_parse_diff_new_ranges` | function | Parses git diff to extract new line ranges for each file |
| `indexer/retrieval.py::_symbols_for_changed_files` | function | Retrieves symbols affected by changed files using manifest |
| `indexer/retrieval.py::_has_config_changes` | function | Checks if config file path has changed using Path and returns bool |
| `indexer/retrieval.py::_has_code_changes` | function | Checks if any code file path has lowercased changes |
| `indexer/retrieval.py::_limit_list` | function | Returns list bounded by min and max length |
| `indexer/retrieval.py::_normalize_source_signature` | function | Normalizes source signature by stripping, substituting, and re-joining lines |
| `indexer/retrieval.py::_is_test_path` | function | Checks if Path matches test file prefixes and suffixes |
| `indexer/retrieval.py::_node_edges` | function | Extracts node edges from parsed JSON lists into a set |
| `indexer/retrieval.py::_stable_id_moves` | function | Computes stable symbol ID moves by sorting and appending changes |
| `indexer/retrieval.py::_extract_graphql_operations` | function | Finds and groups GraphQL operation names using regex, returns deduplicated list |
| `indexer/retrieval.py::_looks_like_client_symbol` | function | Determines if symbol name is likely a client symbol by lowercasing and joining |
| `indexer/retrieval.py::_repo_nodes_for_graph` | function | Loads repository manifest and fetches nodes by IDs for graph construction |
| `indexer/retrieval.py::_parse_json_list` | function | Parses JSON string into Python list using json.loads |
| `indexer/ruby_parser.py::_get_ruby_language` | function | Initializes tree-sitter Ruby language object |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function | Extracts Ruby comments from node text |
| `indexer/ruby_parser.py::_extract_imports` | function | Collects require/include paths from Ruby node |
| `indexer/ruby_parser.py::_extract_calls` | function | Collects method call identifiers from Ruby node |
| `indexer/ruby_parser.py::_get_name` | function | Returns name from Ruby node's name child |
| `indexer/ruby_parser.py::parse_ruby_file` | function | Parses Ruby file into AST nodes with metadata |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/ruby_parser.py::visit` | function | Recursively builds ASTNode tree for Ruby file |
| `indexer/rust_parser.py::_get_rust_language` | function | Initializes tree-sitter Rust language object |
| `indexer/rust_parser.py::_extract_rust_doc` | function | Extracts Rust doc comments from node text |
| `indexer/rust_parser.py::_extract_imports` | function | Collects import paths from Rust source node children |
| `indexer/rust_parser.py::_extract_calls` | function | Collects function call identifiers from node |
| `indexer/rust_parser.py::_get_name` | function | Returns name from node's name child |
| `indexer/rust_parser.py::parse_rust_file` | function | Parses Rust file into AST nodes with metadata |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/rust_parser.py::visit` | function | Recursively builds ASTNode tree from parsed tree |
| `indexer/utils.py::resolve_api_key` | function | Retrieves API key and replaces characters, checks uppercase |
| `indexer/utils.py::_rel` | function | Converts path to relative string using relative_to |
| `indexer/utils.py::_node_text` | function | Decodes node text from bytes to string |
| `indexer/utils.py::load_env_file` | function | Reads .env file and returns dict of key-value pairs |
| `indexer/vector_store.py::_get_client` | function | Returns PersistentClient for vector store, creating if missing |
| `indexer/vector_store.py::evict_client` | function | Removes cached ChromaDB client for given repo |
| `indexer/vector_store.py::_get_or_create_collection` | function | Gets or creates ChromaDB collection by name with error recovery |
| `indexer/vector_store.py::upsert_nodes` | function | Upserts symbol nodes into ChromaDB collection with metadata |
| `indexer/vector_store.py::search` | function | Queries ChromaDB collection for similar embeddings and returns results |
| `indexer/vector_store.py::get_by_ids` | function | Retrieves documents from ChromaDB collection by their IDs |
| `indexer/vector_store.py::delete_by_files` | function | Deletes all documents for given file paths from the vector store collection |
| `indexer/vector_store.py::_build_doc` | function | Constructs a Document object by reading file content and appending metadata |
| `indexer/vector_store.py::_truncate_list` | function | Truncates a list to maximum length and logs truncated items as compact JSON |
| `indexer/vector_store.py::_build_meta` | function | Builds metadata dictionary for an AST node including entry point kind and symbol ID |
| `indexer/vector_store.py::json_dumps_compact` | function | Serializes object to compact JSON string without whitespace |
| `indexer/vector_store.py::_infer_entry_point_kind` | function | Infers entry point kind from decorator names in an AST node |
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
| `indexer/cache.py::_get_shard_lock` | function | Returns a threading Lock for a shard key to synchronize cache access |
| `indexer/cache.py::_atomic_write_json` | function | Atomically writes JSON data to a file using temporary file and replace |
| `indexer/cache.py::ShardedCache` | class | Manages a sharded on-disk cache for parsed AST nodes |
| `indexer/cache.py::ShardedCache.__init__` | method | Initializes the ShardedCache with root directory and max shard size |
| `indexer/cache.py::ShardedCache._dir` | method | Ensures the shard directory exists creating it if needed |
| `indexer/cache.py::ShardedCache._legacy_path` | method | Returns the legacy single-file cache path from cache config |
| `indexer/cache.py::ShardedCache.load` | method | Loads all cache shards from disk into a single dictionary |
| `indexer/cache.py::ShardedCache.save` | method | Saves the in-memory cache to sharded JSON files atomically |
| `indexer/git_ops.py::GitOperationError` | class | Custom exception class for Git operation failures |
| `indexer/git_ops.py::GitOperationError.__init__` | method | Initializes GitOperationError with message via parent Exception |
| `indexer/git_ops.py::git_fetch_checkout_pull` | function | Fetches and checks out a branch with pull, cleanup on error. |
| `indexer/git_ops.py::_detect_default_branch` | function | Detects default branch name from remote Git refs. |
| `indexer/git_ops.py::_match_branch_rule` | function | Matches a branch name against a glob pattern using fnmatch. |
| `indexer/git_ops.py::_discover_remote_branches` | function | Discovers remote branches matching configured rules. |
| `indexer/git_ops.py::_inject_credentials` | function | Injects credentials into a Git remote URL by parsing and quoting. |
| `indexer/git_ops.py::_sanitize_error` | function | Sanitizes error messages by removing credentials and secrets. |
| `indexer/git_ops.py::_store_credentials` | function | Stores credentials in .git-credentials file with secure permissions. |
| `indexer/git_ops.py::_err` | function | Raises GitOperationError with sanitized error message. |
| `indexer/git_ops.py::_cleanup_worktree` | function | Removes a temporary Git worktree directory using run. |
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
| `indexer/task_store.py::TaskStore` | class | In-memory task storage with TTL-based cleanup |
| `indexer/task_store.py::TaskStore.__init__` | method | Initializes empty tasks dict and threading Lock |
| `indexer/task_store.py::TaskStore._cleanup` | method | Removes tasks older than TTL from store |
| `indexer/task_store.py::TaskStore.create` | method | Creates new task with UUID and current timestamp |
| `indexer/task_store.py::TaskStore.get` | method | Returns deep copy of task by ID |
| `indexer/task_store.py::TaskStore.update` | method | Updates task status and sets current timestamp |
| `indexer/agent_context.py::resolve_symbol` | function | Resolves a natural language query to a symbol ID using search and alias scoring. |
| `indexer/agent_context.py::impact_analysis` | function | Analyzes impact of symbol change by tracing calls and finding tests. |
| `indexer/agent_context.py::change_plan` | function | Generates a change plan with impact analysis, freshness risks, and pre-edit checks. |
| `indexer/agent_context.py::list_entry_points` | function | Lists entry points (public APIs, endpoints) from indexed symbols and manifest. |
| `indexer/agent_context.py::locate_from_error` | function | Locates code symbols from error messages by extracting frames and HTTP paths. |
| `indexer/agent_contracts.py::agent_capabilities_manifest` | function | Assembles agent capabilities manifest with input schema, output, examples, and next tools. |
| `indexer/agent_contracts.py::agent_schema` | function | Builds the full agent JSON schema including capabilities and endpoint specs. |
| `indexer/agent_contracts.py::_capability_input_schema` | function | Builds input JSON schema for a capability using object schema. |
| `indexer/agent_contracts.py::_capability_required_output` | function | Extracts required output schema from a capability configuration. |
| `indexer/agent_contracts.py::_capability_example` | function | Extracts example from a capability configuration. |
| `indexer/agent_contracts.py::_capability_next_tools` | function | Extracts next tools list from a capability configuration. |
| `indexer/agent_contracts.py::_object_schema` | function | Builds JSON object schema by mapping fields to their schemas. |
| `indexer/agent_contracts.py::_field_schema` | function | Builds JSON field schema interpreting type suffixes as arrays or objects. |
| `indexer/agent_contracts.py::_agent_json_schema` | function | Builds the agent JSON schema structure by iterating over schema items. |
| `indexer/agent_contracts.py::_endpoint_specs` | function | Builds endpoint specifications from configuration items. |
| `indexer/agent_diagnostics.py::diagnose_index` | function | Diagnoses index health by checking file existence, freshness, and stats. |
| `indexer/agent_diff.py::post_edit_verify` | function | Verifies post-edit by checking config/code changes and recommending test commands. |
| `indexer/agent_diff.py::stable_symbol_id` | function | Computes a stable symbol ID using file path, source signature, and SHA1 hashing. |
| `indexer/agent_diff.py::change_set` | function | Creates a change set combining impact analysis, post-edit verification, and test recommendations. |
| `indexer/agent_diff.py::coverage_map` | function | Maps symbol coverage by finding test files for each symbol from the index. |
| `indexer/agent_diff.py::index_diff_report` | function | Reports diff between index snapshots showing moved symbols and node edges. |
| `indexer/agent_graph.py::cross_repo_graph` | function | Builds cross-repo dependency graph by detecting client symbols, HTTP paths, and GraphQL operations. |
| `indexer/rest_api.py::register_repo` | function |  |
| `indexer/rest_api.py::task_status` | function |  |
| `indexer/rest_api.py::validate_repo` | function |  |
| `indexer/rest_api.py::sync_repo` | function |  |
| `indexer/rest_api.py::rebuild_repo` | function |  |
| `indexer/rest_api.py::_run_all_branches` | function |  |
| `indexer/rest_api.py::sync_all_branches` | function |  |
| `indexer/rest_api.py::reindex_repo` | function |  |
| `indexer/rest_api.py::rebuild_all_branches` | function |  |
| `indexer/rest_api.py::_run_indexing_pipeline` | function |  |
| `indexer/rest_api.py::_run_rebuild_task` | function |  |
| `indexer/rest_api.py::_run_rebuild_task_inner` | function |  |
| `indexer/rest_api.py::_run_sync_task` | function |  |
| `indexer/rest_api.py::_run_register_task` | function |  |
| `indexer/rest_api.py::_run_register_task_inner` | function |  |
| `indexer/rest_api.py::_is_managed_repo_root` | function |  |
| `indexer/rest_api.py::unregister_repo` | function |  |
| `indexer/rest_api.py::search_symbols` | function |  |
| `indexer/rest_api.py::trace_call` | function |  |
| `indexer/rest_api.py::get_source_context` | function |  |
| `indexer/rest_api.py::get_edit_context` | function |  |
| `indexer/rest_api.py::resolve_symbol` | function |  |
| `indexer/rest_api.py::find_tests_for_symbol` | function |  |
| `indexer/rest_api.py::pre_edit_check` | function |  |
| `indexer/rest_api.py::impact_analysis` | function |  |
| `indexer/rest_api.py::change_plan` | function |  |
| `indexer/rest_api.py::diagnose_index` | function |  |
| `indexer/rest_api.py::agent_protocol` | function |  |
| `indexer/rest_api.py::locate_from_error` | function |  |
| `indexer/rest_api.py::list_entry_points` | function |  |
| `indexer/rest_api.py::post_edit_verify` | function |  |
| `indexer/rest_api.py::change_set` | function |  |
| `indexer/rest_api.py::coverage_map` | function |  |
| `indexer/rest_api.py::index_diff_report` | function |  |
| `indexer/rest_api.py::cross_repo_graph` | function |  |
| `indexer/rest_api.py::agent_capabilities` | function |  |
| `indexer/rest_api.py::agent_schema` | function |  |
| `indexer/rest_api.py::stable_symbol_id_endpoint` | function |  |
| `indexer/rest_api.py::index_status` | function |  |
| `indexer/rest_api.py::list_repos` | function |  |
| `indexer/rest_api.py::health` | function |  |
| `indexer/rest_api.py::repo_detail` | function |  |
| `indexer/rest_api.py::wiki_page_content` | function |  |
| `indexer/rest_api.py::update_repo_meta` | function |  |
| `indexer/rest_api.py::multi_repo_skill` | function |  |
| `indexer/rest_api.py::_get_webhook_url` | function |  |
| `indexer/rest_api.py::_webhook_sign` | function |  |
| `indexer/rest_api.py::_verify_webhook_sign` | function |  |
| `indexer/rest_api.py::webhook_by_name` | function |  |
| `indexer/rest_api.py::create_app` | function |  |
| `indexer/rest_api.py::_index_page` | function |  |
| `indexer/rest_api.py::_resolve_repos` | function |  |
| `indexer/rest_api.py::_trace_call_impl` | function |  |
| `indexer/rest_api.py::_expand_with_call_graph` | function |  |
| `indexer/rest_api.py::_InvalidBodyError` | class |  |
| `indexer/rest_api.py::_validate_diff_payload` | function |  |
| `indexer/rest_api.py::_parse_body` | function |  |
| `indexer/rest_api.py::_LoggingMiddleware` | class |  |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method |  |
| `indexer/rest_api.py::_invalid_body_handler` | function |  |
| `indexer/rest_api.py::_AuthMiddleware` | class |  |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method |  |
## Data Flows
- CLI `run` → load existing nodes, identify stale files, re-parse changed files, deep enrich index (embeddings, cross-references) → write wiki pages and update manifest.
- Agent context request → `get_edit_context` → loads LLM, retrieves relevant symbols from vector store, bundles snippets → returns JSON context.
- MCP server request → `create_server` → exposes tools for semantic search, symbol lookup, and change planning → queries vector store and AST cache.
- REST API `/search` → `create_app` → loads repo registry, runs vector search, returns results.
## Design Constraints
- Embedding model is configured via `EmbeddingConfig`; changing it invalidates all stored embeddings and requires a full re-index.
- `compute_hash_short` uses first 8 hex chars of SHA256; collisions are practically improbable for file-level change detection but not guaranteed.
- AST caching uses atomic writes to avoid partial corruption, but the cache is not synchronized across processes — concurrent CLI runs may overwrite.
- Stale file detection relies on git diff against HEAD; untracked files are not considered unless staged.
- Agent `change_plan` requires LLM availability; if LLM fails, it falls back to a heuristic structural plan but may miss semantic implications.
- `agent_diff` expects unified diff format from git; non-standard diffs (e.g., from `--no-index`) may cause parsing failures.
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, FastMCP, FileEntry, GitOperationError, HTMLResponse, IndexEntry, JSONResponse, Language, Lock, Manifest, Middleware, NamedTemporaryFile, OpenAI, PageContext, Parser, Path, PersistentClient, RLock, Request, Route, Starlette, StaticFiles, ThreadPoolExecutor, ValueError, VectorStoreConfig, _EmptyResponseError, _InvalidBodyError, _MCPAuthMiddleware, __init__, _agent_capabilities_manifest_impl, _agent_json_schema, _agent_protocol_bundle_impl, _agent_schema_impl, _annotate_match_reasons, _anthropic_completion, _api_get, _api_post, _api_request, _apply_env, _apply_env_field, _apply_mcp_auth, _atomic_write_json, _atomic_write_text, _build_doc, _build_meta, _call_embedding_api, _capability_example, _capability_input_schema, _capability_next_tools, _capability_required_output, _change_plan_impl, _change_set_impl, _cleanup, _cleanup_worktree, _collect_affected_files, _coverage_map_impl, _cross_repo_graph_impl, _desc_cache, _detect_default_branch, _diagnose_index_impl, _discover_remote_branches, _emb_cache, _endpoint_specs, _ensure_cache_gitignore, _entry_point_from_decorators, _env, _env_int, _err, _expand_retrieval, _expand_with_call_graph, _extract_calls, _extract_error_frames, _extract_error_terms, _extract_go_doc, _extract_graphql_operations, _extract_http_paths, _extract_imports, _extract_javadoc, _extract_jsdoc, _extract_ruby_doc, _extract_rust_doc, _fdesc_cache, _field_schema, _find_tests_for_symbol_impl, _freshness_risks, _get_anthropic_client, _get_class_method_ids, _get_client, _get_edit_context_impl, _get_go_language, _get_index_status_impl, _get_java_language, _get_language, _get_name, _get_openai_client, _get_or_create_collection, _get_receiver, _get_repo_lock, _get_ruby_language, _get_rust_language, _get_shard_lock, _get_webhook_url, _git_diff, _git_dirty_files, _has_code_changes, _has_config_changes, _hook_command, _hook_script_append, _hook_script_fresh, _impact_analysis_impl, _impl, _index_diff_report_impl, _infer_entry_point_kind, _infer_entry_point_kind_from_hit, _inject_credentials, _is_anthropic, _is_indexable, _is_managed_repo_root, _is_test_path, _jinja_env, _json_dumps, _limit_list, _list_entry_points_impl, _litellm_completion, _litellm_kwargs, _load_one, _locate_from_error_impl, _looks_like_client_symbol, _looks_like_entry_point, _manifest, _match_branch_rule, _natural_language_alias_score, _node_edges, _node_text, _normalize_source_signature, _object_schema, _orig_method, _parse_body, _parse_diff_changed_files, _parse_diff_new_ranges, _parse_json_list, _parse_llm_json, _post_edit_verify_impl, _pre_edit_check_impl, _rel, _repo_nodes_for_graph, _resolve_api_key, _resolve_repos, _resolve_symbol_impl, _run, _run_all_branches, _run_checked, _run_indexing_pipeline, _run_rebuild_task_inner, _run_register_task_inner, _sanitize_error, _save, _shard_fn, _should_use_anthropic_sdk, _stable_id_moves, _stable_symbol_id_impl, _store_credentials, _symbols_for_changed_files, _trace_call_impl, _trace_call_retrieval, _truncate_list, _validate_diff_payload, _verify_webhook_sign, _webhook_sign, acquire, add, agent_capabilities_manifest, agent_protocol_bundle, agent_schema, all, all_tracked_files, any, append, as_completed, asdict, body, bool, build_batches, build_embedding_text, build_index, build_page, call_next, change_plan, change_set, changed_files_since, child_by_field_name, chmod, command, compare_digest, compile, completion, compute_ast_sig, compute_embedding_sig, compute_hash, compute_hash_short, count, coverage_map, create, create_api_server, create_app, create_server, cross_reference, cross_repo_graph, current_branch, current_commit, cwd, debug, decode, deep_enrich_index, deep_enrich_pages, deepcopy, defaultdict, delete, density_group, diagnose_index, dict, dump, dumps, echo, embed_nodes, embed_query, encode, endswith, enumerate, error, evict_client, exists, extend, find_tests_for_symbol, findall, finditer, float, fnmatch, folder_of, fromkeys, get, get_by_ids, get_collection, get_docstring, get_edit_context, get_index_status, get_or_create_collection, get_running_loop, get_source_context, get_template, getattr, gettempdir, git_fetch_checkout_pull, glob, group, hasattr, hexdigest, id, impact_analysis, index_diff_report, info, install_hook, int, is_dir, is_file, is_git_repo, is_relative_to, isdigit, isinstance, isoformat, isupper, items, iter, iterdir, join, json, json_dumps_compact, keys, language, language_tsx, language_typescript, len, list, list_entry_points, list_names, load, load_cached_descriptions, load_cached_embeddings, load_cached_file_descriptions, load_cached_nodes, load_config, load_env_file, load_existing_nodes, load_manifest, loads, locate_from_error, locked, lower, lstrip, match, max, min, mkdir, mount, new, next, now, open, option, parse, parse_candidates, parse_go_file, parse_java_file, parse_js_file, parse_ruby_file, parse_rust_file, pop, post_edit_verify, pre_edit_check, prefixes, prepare_descriptions, progress_callback, query, quote, range, read, read_bytes, read_text, recommend_test_commands, register, relative_to, release, remove_hook, removed_files, removeprefix, removesuffix, render, replace, resolve, resolve_api_key, resolve_group, resolve_symbol, resolve_wiki_page_path, result, rewrite_query, rfind, rglob, rmtree, round, rsplit, rstrip, run, run_fn, run_in_executor, sanitize_fn, sanitize_group_label, save, save_cached_descriptions, save_cached_embeddings, save_cached_file_descriptions, save_cached_nodes, save_config, save_manifest, search, search_symbols, set, setdefault, sha1, sha256, sleep, sort, sorted, split, splitlines, stable_symbol_id, staged_files, stale_files, startswith, stat, str, strftime, strip, sub, submit, sum, super, synthesize_commit_message, time, tool, trace_call, truncate_documents, uniform, unlink, unregister, update, update_manifest, update_meta, upsert, upsert_vectors, urlopen, urlparse, urlunparse, uuid4, values, visit, vs_delete, vs_upsert, walk, warn, warning, with_suffix, write, write_index, write_index_and_skill, write_page, write_text, write_wiki_pages, zip
- **Called by:** indexer/agent_context.py::change_plan, indexer/agent_context.py::impact_analysis, indexer/agent_context.py::list_entry_points, indexer/agent_context.py::locate_from_error, indexer/agent_context.py::resolve_symbol, indexer/agent_contracts.py::_capability_input_schema, indexer/agent_contracts.py::_object_schema, indexer/agent_contracts.py::agent_capabilities_manifest, indexer/agent_contracts.py::agent_schema, indexer/agent_diagnostics.py::diagnose_index, indexer/agent_diff.py::change_set, indexer/agent_diff.py::coverage_map, indexer/agent_diff.py::index_diff_report, indexer/agent_diff.py::post_edit_verify, indexer/agent_diff.py::stable_symbol_id, indexer/agent_graph.py::cross_repo_graph, indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/ast_parser.py::save_cached_nodes, indexer/cache.py::ShardedCache.save, indexer/cli.py::agent_capabilities, indexer/cli.py::agent_context, indexer/cli.py::agent_diagnose, indexer/cli.py::agent_plan, indexer/cli.py::agent_schema, indexer/cli.py::agent_verify, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::compute_embedding_sig, indexer/embedding.py::embed_nodes, indexer/embedding.py::embed_query, indexer/git.py::_run, indexer/git.py::_run_checked, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_branch, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/git_ops.py::_cleanup_worktree, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_err, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_name, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/indexing.py::_load_one, indexer/indexing.py::load_existing_nodes, indexer/indexing.py::parse_candidates, indexer/indexing.py::prepare_descriptions, indexer/indexing.py::update_manifest, indexer/indexing.py::upsert_vectors, indexer/indexing.py::write_index_and_skill, indexer/indexing.py::write_wiki_pages, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_name, indexer/java_parser.py::_get_type_name, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::_anthropic_completion, indexer/llm.py::_describe_files_chunk, indexer/llm.py::_litellm_completion, indexer/llm.py::_resolve_api_key, indexer/llm.py::_should_use_anthropic_sdk, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_nodes_batch, indexer/llm.py::rewrite_query, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::_check, indexer/manifest.py::load_manifest, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::agent_capabilities_manifest_tool, indexer/mcp_server.py::agent_protocol_tool, indexer/mcp_server.py::change_plan_tool, indexer/mcp_server.py::change_set_tool, indexer/mcp_server.py::coverage_map_tool, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::cross_repo_graph_tool, indexer/mcp_server.py::diagnose_index_tool, indexer/mcp_server.py::find_tests_for_symbol_tool, indexer/mcp_server.py::get_edit_context_tool, indexer/mcp_server.py::get_index_status_tool, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::impact_analysis_tool, indexer/mcp_server.py::index_diff_report_tool, indexer/mcp_server.py::list_entry_points_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::locate_from_error_tool, indexer/mcp_server.py::post_edit_verify_tool, indexer/mcp_server.py::pre_edit_check_tool, indexer/mcp_server.py::resolve_symbol_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::stable_symbol_id_tool, indexer/mcp_server.py::trace_call_tool, indexer/repo_registry.py::RepoRegistry._load, indexer/repo_registry.py::RepoRegistry.register, indexer/repo_registry.py::RepoRegistry.unregister, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_run_all_branches, indexer/rest_api.py::_run_indexing_pipeline, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::agent_protocol, indexer/rest_api.py::change_plan, indexer/rest_api.py::change_set, indexer/rest_api.py::coverage_map, indexer/rest_api.py::cross_repo_graph, indexer/rest_api.py::diagnose_index, indexer/rest_api.py::find_tests_for_symbol, indexer/rest_api.py::get_edit_context, indexer/rest_api.py::get_source_context, indexer/rest_api.py::impact_analysis, indexer/rest_api.py::index_diff_report, indexer/rest_api.py::index_status, indexer/rest_api.py::list_entry_points, indexer/rest_api.py::list_repos, indexer/rest_api.py::locate_from_error, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::post_edit_verify, indexer/rest_api.py::pre_edit_check, indexer/rest_api.py::rebuild_all_branches, indexer/rest_api.py::rebuild_repo, indexer/rest_api.py::register_repo, indexer/rest_api.py::reindex_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::resolve_symbol, indexer/rest_api.py::search_symbols, indexer/rest_api.py::stable_symbol_id_endpoint, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::_git_diff, indexer/retrieval.py::_git_dirty_files, indexer/retrieval.py::_infer_entry_point_kind_from_hit, indexer/retrieval.py::_node_edges, indexer/retrieval.py::_parse_diff_new_ranges, indexer/retrieval.py::_repo_nodes_for_graph, indexer/retrieval.py::_symbols_for_changed_files, indexer/retrieval.py::agent_protocol_bundle, indexer/retrieval.py::find_tests_for_symbol, indexer/retrieval.py::get_edit_context, indexer/retrieval.py::get_index_status, indexer/retrieval.py::pre_edit_check, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_name, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_name, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/vector_store.py::_build_meta, indexer/vector_store.py::_infer_entry_point_kind, indexer/vector_store.py::_truncate_list, indexer/vector_store.py::delete_by_files, indexer/vector_store.py::get_by_ids, indexer/vector_store.py::search, indexer/vector_store.py::upsert_nodes, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::resolve_wiki_page_path, indexer/wiki.py::write_index, indexer/wiki.py::write_page, tests/test_agent_context.py::test_agent_capabilities_manifest_lists_local_and_remote_tools, tests/test_agent_context.py::test_agent_protocol_bundle_is_compact_and_includes_freshness, tests/test_agent_context.py::test_change_plan_returns_agent_edit_steps_and_commands, tests/test_agent_context.py::test_change_set_combines_target_impact_tests_and_post_edit, tests/test_agent_context.py::test_change_set_respects_max_results_and_summary, tests/test_agent_context.py::test_coverage_map_links_tests_to_source_symbols, tests/test_agent_context.py::test_coverage_map_repo_wide_respects_max_results, tests/test_agent_context.py::test_cross_repo_graph_links_client_to_backend_route, tests/test_agent_context.py::test_cross_repo_graph_links_graphql_operation, tests/test_agent_context.py::test_cross_repo_graph_respects_max_results, tests/test_agent_context.py::test_diagnose_index_reports_missing_wiki_vector_and_missing_sources, tests/test_agent_context.py::test_diff_payload_size_guard_rejects_oversized_diff, tests/test_agent_context.py::test_find_tests_for_symbol_matches_file_and_symbol, tests/test_agent_context.py::test_get_edit_context_includes_source_relations_tests_and_status, tests/test_agent_context.py::test_impact_analysis_collects_transitive_relations_tests_and_files, tests/test_agent_context.py::test_index_diff_report_compares_symbol_sets, tests/test_agent_context.py::test_index_diff_report_detects_rename_by_stable_id, tests/test_agent_context.py::test_index_status_reports_stale_manifest_entry, tests/test_agent_context.py::test_list_entry_points_reads_first_class_metadata, tests/test_agent_context.py::test_locate_from_error_matches_http_path_to_entry_point, tests/test_agent_context.py::test_locate_from_error_uses_stack_trace_file_and_line, tests/test_agent_context.py::test_post_edit_verify_maps_diff_to_symbols_tests_and_reindex, tests/test_agent_context.py::test_pre_edit_check_reports_dirty_files_and_test_commands, tests/test_agent_context.py::test_resolve_symbol_ranks_exact_name_and_path, tests/test_agent_context.py::test_resolve_symbol_uses_natural_language_alias_reasons, tests/test_agent_context.py::test_search_symbols_can_explain_hits, tests/test_agent_context.py::test_stable_symbol_id_is_deterministic_and_metadata_includes_it, tests/test_agent_context.py::test_vector_metadata_marks_entry_points, tests/test_agent_e2e.py::test_agent_error_to_verify_flow_on_small_repo, tests/test_api_contracts.py::test_agent_capabilities_all_tools_have_schemas, tests/test_api_contracts.py::test_agent_capabilities_endpoint_contract, tests/test_api_contracts.py::test_agent_schema_endpoint_exports_machine_readable_contract, tests/test_api_contracts.py::test_core_tool_contract_top_level_keys, tests/test_api_contracts.py::test_post_edit_verify_endpoint_rejects_oversized_diff, tests/test_api_contracts.py::test_stable_symbol_id_endpoint_contract, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_python_click_command_entry_point, tests/test_ast_parser.py::test_python_fastapi_route_entry_point, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default, tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic, tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic, tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks, tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset, tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset, tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers, tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped, tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped, tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max, tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty, tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty, tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent, tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register, tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister, tests/test_p1_fixes.py::TestRound16Fixes.test_destructive_git_cleanup_before_checkout, tests/test_p1_fixes.py::TestRound16Fixes.test_destructive_git_cleanup_before_pull_without_branch, tests/test_p1_fixes.py::TestRound16Fixes.test_reindex_allows_index_only_request, tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix, tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause, tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks, tests/test_p1_fixes.py::TestTaskStore.test_create_task, tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none, tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp, tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop, tests/test_p1_fixes.py::TestTaskStore.test_update_task, tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock, tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated, tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json, tests/test_p1_fixes.py::run, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, asyncio, chromadb, click, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, copy, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch, fnmatch.fnmatch, hashlib, hmac, indexer.agent_context.change_plan, indexer.agent_context.get_edit_context, indexer.agent_context.impact_analysis, indexer.agent_context.list_entry_points, indexer.agent_context.locate_from_error, indexer.agent_context.resolve_symbol, indexer.agent_contracts.agent_capabilities_manifest, indexer.agent_contracts.agent_schema, indexer.agent_diagnostics.diagnose_index, indexer.agent_diff.change_set, indexer.agent_diff.coverage_map, indexer.agent_diff.index_diff_report, indexer.agent_diff.post_edit_verify, indexer.agent_diff.stable_symbol_id, indexer.agent_graph.cross_repo_graph, indexer.agent_protocol.agent_capabilities_manifest, indexer.agent_protocol.agent_schema, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cache.ShardedCache, indexer.cache._atomic_write_json, indexer.cli._ensure_cache_gitignore, indexer.cli._is_indexable, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.VectorStoreConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_nodes, indexer.embedding.embed_query, indexer.git._GIT_ENV, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.git_ops.GitOperationError, indexer.git_ops._detect_default_branch, indexer.git_ops._discover_remote_branches, indexer.git_ops._inject_credentials, indexer.git_ops._match_branch_rule, indexer.git_ops._sanitize_error, indexer.git_ops._store_credentials, indexer.git_ops.git_fetch_checkout_pull, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing._collect_affected_files, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.prepare_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.rewrite_query, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.repo_registry.RepoRegistry, indexer.repo_registry._get_repo_lock, indexer.repo_registry._locks_lock, indexer.repo_registry._repo_locks, indexer.rest_api.create_app, indexer.retrieval, indexer.retrieval._annotate_match_reasons, indexer.retrieval._expand_with_call_graph, indexer.retrieval._extract_error_frames, indexer.retrieval._extract_error_terms, indexer.retrieval._extract_graphql_operations, indexer.retrieval._extract_http_paths, indexer.retrieval._freshness_risks, indexer.retrieval._git_diff, indexer.retrieval._has_code_changes, indexer.retrieval._has_config_changes, indexer.retrieval._infer_entry_point_kind_from_hit, indexer.retrieval._is_test_path, indexer.retrieval._limit_list, indexer.retrieval._looks_like_client_symbol, indexer.retrieval._looks_like_entry_point, indexer.retrieval._natural_language_alias_score, indexer.retrieval._node_edges, indexer.retrieval._normalize_source_signature, indexer.retrieval._parse_diff_changed_files, indexer.retrieval._parse_diff_new_ranges, indexer.retrieval._parse_json_list, indexer.retrieval._repo_nodes_for_graph, indexer.retrieval._stable_id_moves, indexer.retrieval._symbols_for_changed_files, indexer.retrieval.agent_capabilities_manifest, indexer.retrieval.agent_protocol_bundle, indexer.retrieval.change_plan, indexer.retrieval.change_set, indexer.retrieval.coverage_map, indexer.retrieval.cross_repo_graph, indexer.retrieval.diagnose_index, indexer.retrieval.find_tests_for_symbol, indexer.retrieval.get_edit_context, indexer.retrieval.get_index_status, indexer.retrieval.get_source_context, indexer.retrieval.impact_analysis, indexer.retrieval.index_diff_report, indexer.retrieval.list_entry_points, indexer.retrieval.locate_from_error, indexer.retrieval.post_edit_verify, indexer.retrieval.pre_edit_check, indexer.retrieval.resolve_symbol, indexer.retrieval.search_symbols, indexer.retrieval.stable_symbol_id, indexer.retrieval.trace_call, indexer.retrieval.truncate_documents, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.task_store.TaskStore, indexer.utils.FATAL_EXCEPTIONS, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.utils.resolve_api_key, indexer.vector_store._get_client, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.get_by_ids, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki._atomic_write_text, indexer.wiki._jinja_env, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.resolve_wiki_page_path, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, logging, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, random, re, shutil, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_go, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_rust, tree_sitter_typescript, typing.Callable, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
## Entry Points
- `main`
- `init`
- `status`
- `agent`
- `agent_context`
- `agent_verify`
- `agent_plan`
- `agent_diagnose`
- `agent_capabilities`
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
- `get_edit_context_tool`
- `resolve_symbol_tool`
- `find_tests_for_symbol_tool`
- `pre_edit_check_tool`
- `impact_analysis_tool`
- `change_plan_tool`
- `diagnose_index_tool`
- `agent_protocol_tool`
- `locate_from_error_tool`
- `list_entry_points_tool`
- `post_edit_verify_tool`
- `change_set_tool`
- `coverage_map_tool`
- `index_diff_report_tool`
- `cross_repo_graph_tool`
- `agent_capabilities_manifest_tool`
- `stable_symbol_id_tool`
- `get_index_status_tool`
- `list_repos`
- `search_symbols_tool`
- `trace_call_tool`
- `get_source_context_tool`
- `get_edit_context_tool`
- `resolve_symbol_tool`
- `find_tests_for_symbol_tool`
- `pre_edit_check_tool`
- `impact_analysis_tool`
- `change_plan_tool`
- `diagnose_index_tool`
- `agent_protocol_tool`
- `locate_from_error_tool`
- `list_entry_points_tool`
- `post_edit_verify_tool`
- `change_set_tool`
- `coverage_map_tool`
- `index_diff_report_tool`
- `cross_repo_graph_tool`
- `agent_capabilities_manifest_tool`
- `stable_symbol_id_tool`
- `get_index_status_tool`
- `upsert_nodes`
- `delete_by_files`
- `ShardedCache`
- `register_repo`
- `task_status`
- `validate_repo`
- `sync_repo`
- `rebuild_repo`
- `sync_all_branches`
- `reindex_repo`
- `rebuild_all_branches`
- `unregister_repo`
- `agent_protocol`
- `agent_capabilities`
- `stable_symbol_id_endpoint`
- `index_status`
- `list_repos`
- `health`
- `repo_detail`
- `wiki_page_content`
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
