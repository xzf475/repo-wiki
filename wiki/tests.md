# tests/

## Modules
| File | Purpose |
|------|---------|
| tests/test_manifest.py | Tests manifest hash computation persistence and stale file detection |
| tests/test_grouper.py | Tests density-based file grouping and wiki page assignment logic |
| tests/fixtures/sample_py/auth.py | Sample fixture implementing OAuth2 token validation and route protection decorators |
| tests/test_config.py | Tests configuration loading default handling and TOML persistence |
| tests/test_ast_parser.py | Validates Python AST parsing symbol extraction and cache functionality |
| tests/test_wiki.py | Tests wiki page and index generation content correctness and file writing |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/fixtures/sample_py/auth.py::TokenValidator` | class | Validates OAuth2 access tokens and manages refresh token rotation |
| `tests/fixtures/sample_py/auth.py::TokenValidator.refresh` | method | Signs and submits refresh payloads to rotate expired OAuth2 credentials |
| `tests/fixtures/sample_py/auth.py::require_auth` | function | Wraps route handlers to enforce authentication checks before execution |
| `tests/fixtures/sample_py/auth.py::wrapper` | function | Executes the wrapped route function after verifying valid authentication credentials |
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function | Verifies parse_file returns a non-empty list of AST nodes |
| `tests/test_ast_parser.py::test_function_node` | function | Asserts parsed output contains at least one function definition node |
| `tests/test_ast_parser.py::test_method_node` | function | Asserts parsed output contains at least one method definition node |
| `tests/test_ast_parser.py::test_class_node` | function | Asserts parsed output contains a class node with correct name suffix |
| `tests/test_ast_parser.py::test_docstring_extracted` | function | Verifies parser extracts and attaches docstrings to parsed AST nodes |
| `tests/test_ast_parser.py::test_imports_extracted` | function | Checks parser correctly identifies and counts imported modules in AST nodes |
| `tests/test_ast_parser.py::test_calls_extracted` | function | Verifies parser extracts function call references from parsed AST nodes |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function | Tests saving and reloading parsed AST nodes preserves original node count |
| `tests/test_config.py::_clean_env` | function | Removes specific environment variables for isolated test execution |
| `tests/test_config.py::_restore_env` | function | Restores original environment variable values after test cleanup |
| `tests/test_config.py::test_load_defaults` | function | Verifies configuration loader applies default values when environment variables are absent |
| `tests/test_config.py::test_save_and_reload` | function | Validates configuration persists correctly to disk and reloads with identical values |
| `tests/test_config.py::test_partial_toml_uses_defaults` | function | Ensures partial TOML files merge correctly with default configuration values |
| `tests/test_grouper.py::test_sparse_folders_merge_to_parent` | function | Verifies low-density folders are merged into their parent directory group |
| `tests/test_grouper.py::test_dense_folder_gets_own_page` | function | Asserts high-density directories generate independent documentation pages instead of merging |
| `tests/test_grouper.py::test_different_folders_get_separate_groups` | function | Confirms distinct top-level folders are assigned to separate grouping buckets |
| `tests/test_grouper.py::test_deep_sparse_merges_upward` | function | Tests deeply nested low-density directories recursively merge into higher parents |
| `tests/test_grouper.py::test_root_level_files` | function | Verifies root-level files are correctly grouped without directory assignment |
| `tests/test_grouper.py::test_returns_all_files` | function | Ensures grouping function output contains every input file exactly once |
| `tests/test_grouper.py::test_root_files_count_correctly` | function | Validates accurate file counts are maintained after root-level grouping operations |
| `tests/test_manifest.py::test_compute_hash_stable` | function | Confirms file hash computation produces identical output for unchanged content |
| `tests/test_manifest.py::test_empty_manifest_on_missing` | function | Verifies manifest loader returns an empty structure when target file is absent |
| `tests/test_manifest.py::test_save_and_reload` | function | Tests manifest serialization and deserialization preserve original file entry data |
| `tests/test_manifest.py::test_stale_files_detected` | function | Asserts modified files are correctly flagged as stale after manifest reload |
| `tests/test_manifest.py::test_fresh_file_not_stale` | function | Verifies unmodified files match stored hashes and are excluded from stale list |
| `tests/test_manifest.py::test_load_manifest_missing_component_ids` | function | Tests manifest loader safely handles and backfills missing component identifier fields |
| `tests/test_wiki.py::_make_node` | function | Constructs mock AST node dictionaries with predefined attributes for test fixtures |
| `tests/test_wiki.py::test_build_page_contains_symbol` | function | Asserts generated wiki page HTML includes the target function symbol name |
| `tests/test_wiki.py::test_build_page_contains_calls` | function | Verifies rendered page output lists all outgoing function call dependencies |
| `tests/test_wiki.py::test_build_page_contains_called_by` | function | Checks rendered page includes incoming caller references in the dependency graph |
| `tests/test_wiki.py::test_build_page_no_agent_hints` | function | Ensures generated page content excludes internal agent hint strings from output |
| `tests/test_wiki.py::test_build_index_contains_page` | function | Validates main documentation index lists all generated page titles correctly |
| `tests/test_wiki.py::test_write_page_creates_file` | function | Confirms write_page outputs sanitized content to a new file on disk |
## Relationships
- **Calls:** ASTNode, Config, FileEntry, IndexEntry, Manifest, NamedTemporaryFile, PageContext, Path, TemporaryDirectory, _clean_env, _make_node, _restore_env, all, any, build_index, build_page, compute_hash, density_group, dict, dumps, endswith, exists, func, isinstance, items, keys, len, load_cached_nodes, load_config, load_manifest, lower, mkdir, next, parse_file, pop, range, read_text, save_cached_nodes, save_config, save_manifest, set, sign_payload, stale_files, startswith, update, values, write, write_bytes, write_page, write_text
- **Called by:** tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** hashlib, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config, indexer.config.Config, indexer.config._ENV_LOADED, indexer.config.load_config, indexer.config.save_config, indexer.grouper.density_group, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, json, os, pathlib.Path, tempfile, utils.crypto.sign_payload
## Entry Points
- `TokenValidator`
- `require_auth`
- `wrapper`
- `test_parse_returns_nodes`
- `test_function_node`
- `test_method_node`
- `test_class_node`
- `test_docstring_extracted`
- `test_imports_extracted`
- `test_calls_extracted`
- `test_cache_roundtrip`
- `test_load_defaults`
- `test_save_and_reload`
- `test_partial_toml_uses_defaults`
- `test_sparse_folders_merge_to_parent`
- `test_dense_folder_gets_own_page`
- `test_different_folders_get_separate_groups`
- `test_deep_sparse_merges_upward`
- `test_root_level_files`
- `test_returns_all_files`
- `test_root_files_count_correctly`
- `test_compute_hash_stable`
- `test_empty_manifest_on_missing`
- `test_save_and_reload`
- `test_stale_files_detected`
- `test_fresh_file_not_stale`
- `test_load_manifest_missing_component_ids`
- `test_build_page_contains_symbol`
- `test_build_page_contains_calls`
- `test_build_page_contains_called_by`
- `test_build_page_no_agent_hints`
- `test_build_index_contains_page`
- `test_write_page_creates_file`
