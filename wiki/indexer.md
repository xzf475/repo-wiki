# indexer/

## Modules
| File | Purpose |
|------|---------|
| indexer/wiki.py | Generates and writes semantic wiki pages and index files for codebases |
| indexer/cli.py | Command-line interface for indexing configuration Git hooks and MCP servers |
| indexer/config.py | Loads validates and saves application and embedding configuration from environment |
| indexer/js_parser.py | Parses JavaScript and TypeScript files using tree-sitter to extract code structure |
| indexer/grouper.py | Groups source files into wiki pages based on directory density thresholds |
| indexer/ast_parser.py | Parses and caches Python AST nodes with import and call extraction |
| indexer/manifest.py | Tracks indexed file hashes and metadata to detect changes and manage caching |
| indexer/git.py | Provides Git operations for tracking commits file changes and repository status |
| indexer/llm.py | Generates LLM code descriptions enriches wiki pages and synthesizes commit messages |
| indexer/hooks.py | Manages pre-commit hook installation updates and removal for the indexer |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/ast_parser.py::ASTNode` | class | Represents parsed AST node data for indexing and caching |
| `indexer/ast_parser.py::_rel` | function | Converts absolute file paths to relative string representations |
| `indexer/ast_parser.py::_extract_imports` | function | Extracts module import names from Python AST node tree |
| `indexer/ast_parser.py::_extract_calls` | function | Extracts function and method call names from Python AST |
| `indexer/ast_parser.py::_get_class_method_ids` | function | Collects AST node IDs of functions directly inside class bodies |
| `indexer/ast_parser.py::parse_file` | function | Parses Python files into ASTNode lists handling syntax errors gracefully |
| `indexer/ast_parser.py::compute_hash_short` | function | Generates 16-character SHA256 hash of file bytes for cache naming |
| `indexer/ast_parser.py::load_cached_nodes` | function | Deserializes cached ASTNode objects from JSON files on disk |
| `indexer/ast_parser.py::save_cached_nodes` | function | Serializes ASTNode dictionaries into JSON files for caching |
| `indexer/cli.py::main` | function | Registers CLI command groups and dispatches execution entry point |
| `indexer/cli.py::init` | function | Initializes project config installs pre-commit hooks and updates documentation |
| `indexer/cli.py::run` | function | Indexes codebase files groups them and renders wiki documentation pages |
| `indexer/cli.py::status` | function | Displays indexing status tracked files and detects stale documentation |
| `indexer/cli.py::hook` | function | Registers CLI subcommand group for managing pre-commit hooks |
| `indexer/cli.py::hook_install` | function | Installs the pre-commit hook script into the git repository |
| `indexer/cli.py::hook_remove` | function | Deletes the pre-commit hook script from the git repository |
| `indexer/cli.py::serve` | function | Launches MCP server for semantic code search operations |
| `indexer/cli.py::serve_api` | function | Launches REST API server for multi-repository semantic code search |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Adds cache directory paths to root gitignore file |
| `indexer/cli.py::_is_indexable` | function | Validates whether a file path matches indexable patterns and extensions |
| `indexer/config.py::_load_env_file` | function | Reads and parses key-value environment variables from dotfiles |
| `indexer/config.py::EmbeddingConfig` | class | Holds configuration parameters for text embedding generation |
| `indexer/config.py::VectorStoreConfig` | class | Stores connection and indexing settings for vector database |
| `indexer/config.py::Config` | class | Aggregates embedding vector store and application settings into one object |
| `indexer/config.py::_env` | function | Retrieves environment variable values with default fallbacks |
| `indexer/config.py::_env_int` | function | Fetches environment variables and casts them to integers |
| `indexer/config.py::load_config` | function | Loads configuration from TOML files and merges environment overrides |
| `indexer/config.py::_apply_env` | function | Overrides configuration object fields with environment variable values |
| `indexer/config.py::save_config` | function | Serializes and writes configuration object to TOML disk file |
| `indexer/git.py::_run` | function | Executes shell git commands and returns trimmed stdout strings |
| `indexer/git.py::current_commit` | function | Retrieves the current git HEAD commit hash |
| `indexer/git.py::staged_files` | function | Lists file paths currently staged in the git index |
| `indexer/git.py::changed_files_since` | function | Returns list of files changed since a target commit |
| `indexer/git.py::all_tracked_files` | function | Lists all files currently tracked by the git repository |
| `indexer/git.py::is_git_repo` | function | Verifies if the current working directory is a git repository |
| `indexer/grouper.py::density_group` | function | Maps files to wiki pages by merging shallow directory groups |
| `indexer/grouper.py::folder_of` | function | Extracts the immediate parent directory string from a file path |
| `indexer/grouper.py::prefixes` | function | Generates all ancestor directory path prefixes from file to root |
| `indexer/grouper.py::resolve_group` | function | Determines the optimal wiki page grouping for a given file |
| `indexer/hooks.py::_hook_command` | function | Constructs the executable command string for the pre-commit hook |
| `indexer/hooks.py::_hook_script_fresh` | function | Generates a new pre-commit hook script with indexer command |
| `indexer/hooks.py::_hook_script_append` | function | Formats indexer command block for appending to existing hook scripts |
| `indexer/hooks.py::install_hook` | function | Installs creates or patches the pre-commit hook with indexer commands |
| `indexer/hooks.py::remove_hook` | function | Removes indexer-managed blocks or files from the git pre-commit hook |
| `indexer/js_parser.py::_rel` | function | Converts absolute file paths to relative string representations |
| `indexer/js_parser.py::_get_language` | function | Loads tree-sitter parser language object for TypeScript or TSX files |
| `indexer/js_parser.py::_node_text` | function | Extracts and decodes raw source text from tree-sitter nodes |
| `indexer/js_parser.py::_extract_jsdoc` | function | Extracts preceding JSDoc comment text blocks from code nodes |
| `indexer/js_parser.py::_extract_imports` | function | Parses and collects import module paths from JS/TS syntax trees |
| `indexer/js_parser.py::_extract_calls` | function | Recursively collects called function names from JS/TS syntax trees |
| `indexer/js_parser.py::_get_name` | function | Retrieves identifier strings from function and class definition nodes |
| `indexer/js_parser.py::parse_js_file` | function | Parses JavaScript and TypeScript files into indexed ASTNode structures |
| `indexer/js_parser.py::visit` | function | Recursively builds ASTNode objects from JS/TS tree-sitter parse trees |
| `indexer/js_parser.py::visit` | function | Recursively builds ASTNode objects from JS/TS tree-sitter parse trees |
| `indexer/js_parser.py::visit` | function | Recursively builds ASTNode objects from JS/TS tree-sitter parse trees |
| `indexer/llm.py::_is_anthropic` | function | Checks if the provided model name belongs to Anthropic |
| `indexer/llm.py::_resolve_api_key` | function | Fetches and normalizes LLM provider API keys from environment |
| `indexer/llm.py::_litellm_kwargs` | function | Constructs configuration dictionary for LiteLLM API client requests |
| `indexer/llm.py::_anthropic_completion` | function | Sends prompt completion requests directly via the Anthropic SDK |
| `indexer/llm.py::describe_nodes` | function | Generates one-line LLM descriptions for AST node batches using Anthropic or LiteLLM with fallbacks |
| `indexer/llm.py::describe_files` | function | Generates LLM-powered one-line descriptions for source files using Anthropic or LiteLLM with error fallbacks |
| `indexer/llm.py::deep_enrich_page` | function | Generates deep contextual summaries for documentation pages using configured LLM providers and JSON parsing |
| `indexer/llm.py::deep_enrich_index` | function | Generates deep contextual summaries for documentation indexes using configured LLM providers and JSON parsing |
| `indexer/llm.py::synthesize_commit_message` | function | Generates concise Git commit messages from code changes using configured LLM providers |
| `indexer/manifest.py::FileEntry` | class | Stores metadata and hash for a tracked project file within the manifest |
| `indexer/manifest.py::Manifest` | class | Tracks project files with hashes and identifies modified or missing stale entries |
| `indexer/manifest.py::Manifest.stale_files` | method | Compares stored file hashes against current filesystem state to return modified paths |
| `indexer/manifest.py::compute_hash` | function | Computes SHA-256 hexadecimal digest of a file's raw byte content |
| `indexer/manifest.py::load_manifest` | function | Parses and reconstructs a FileEntry manifest from a JSON file with missing field defaults |
| `indexer/manifest.py::save_manifest` | function | Serializes FileEntry objects to JSON and writes the manifest to disk |
| `indexer/wiki.py::PageContext` | class | Holds structured AST node data and relationships for wiki page generation |
| `indexer/wiki.py::IndexEntry` | class | Stores metadata and file paths for generating documentation index pages |
| `indexer/wiki.py::_jinja_env` | function | Configures and returns a Jinja2 Environment for rendering documentation templates |
| `indexer/wiki.py::build_page` | function | Renders a documentation page template with sorted AST node context and relationships |
| `indexer/wiki.py::build_index` | function | Renders the main documentation index template using configured Jinja2 environment |
| `indexer/wiki.py::write_page` | function | Sanitizes page content and writes it to a directory-safe file path |
| `indexer/wiki.py::write_index` | function | Writes the generated documentation index content to a target file on disk |
## Relationships
- **Calls:** ASTNode, Anthropic, Choice, Config, EmbeddingConfig, Environment, FileEntry, FileSystemLoader, IndexEntry, Language, Manifest, PageContext, Parser, Path, VectorStoreConfig, _anthropic_completion, _apply_env, _ensure_cache_gitignore, _env, _env_int, _extract_calls, _extract_imports, _extract_jsdoc, _get_class_method_ids, _get_language, _get_name, _hook_command, _hook_script_append, _hook_script_fresh, _is_anthropic, _is_indexable, _jinja_env, _litellm_kwargs, _load_env_file, _node_text, _rel, _resolve_api_key, _run, add, all_tracked_files, any, append, asdict, build_index, build_page, changed_files_since, child_by_field_name, chmod, command, completion, compute_hash, compute_hash_short, create, create_app, create_server, current_commit, cwd, decode, deep_enrich_index, deep_enrich_page, defaultdict, density_group, describe_files, describe_nodes, dump, dumps, echo, embed_nodes, enumerate, exists, extend, fnmatch, folder_of, get, get_docstring, get_template, group, hexdigest, id, install_hook, int, is_dir, is_git_repo, isinstance, isoformat, isupper, items, iterdir, join, language, language_tsx, language_typescript, len, list, load, load_cached_nodes, load_config, load_manifest, loads, lower, lstrip, mkdir, now, open, option, parse, parse_file, parse_js_file, prefixes, range, read_bytes, read_text, relative_to, remove_hook, removeprefix, removesuffix, render, replace, resolve, resolve_group, rstrip, run, save_cached_nodes, save_config, save_manifest, set, setdefault, sha256, sorted, split, splitlines, staged_files, stale_files, startswith, str, strftime, strip, sum, synthesize_commit_message, unlink, update, values, visit, vs_upsert, walk, warn, write_index, write_page, write_text
- **Called by:** indexer/ast_parser.py::load_cached_nodes, indexer/ast_parser.py::parse_file, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::load_config, indexer/git.py::_run, indexer/git.py::all_tracked_files, indexer/git.py::changed_files_since, indexer/git.py::current_commit, indexer/git.py::is_git_repo, indexer/git.py::staged_files, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_name, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/llm.py::deep_enrich_index, indexer/llm.py::deep_enrich_page, indexer/llm.py::describe_files, indexer/llm.py::describe_nodes, indexer/llm.py::synthesize_commit_message, indexer/manifest.py::Manifest.stale_files, indexer/manifest.py::load_manifest, indexer/wiki.py::build_index, indexer/wiki.py::build_page, tests/test_ast_parser.py::test_cache_roundtrip, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_manifest.py::test_compute_hash_stable, tests/test_manifest.py::test_empty_manifest_on_missing, tests/test_manifest.py::test_fresh_file_not_stale, tests/test_manifest.py::test_load_manifest_missing_component_ids, tests/test_manifest.py::test_save_and_reload, tests/test_manifest.py::test_stale_files_detected, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, anthropic, ast, click, collections.defaultdict, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.datetime, datetime.timezone, fnmatch.fnmatch, hashlib, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_nodes, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.js_parser.parse_js_file, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_page, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, litellm, os, pathlib.Path, subprocess, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_javascript, tree_sitter_typescript, typing.Optional, uvicorn, warnings
## Entry Points
- `main`
- `init`
- `status`
- `hook`
- `hook_install`
- `hook_remove`
- `serve`
- `serve_api`
