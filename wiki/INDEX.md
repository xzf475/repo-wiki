# Codebase Index

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/indexer.md | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/git.py, indexer/grouper.py, indexer/hooks.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/wiki.py | main, init, status, hook, hook_install, hook_remove, serve, serve_api, Manifest.stale_files |
| wiki/tests.md | tests/fixtures/sample_py/auth.py, tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_wiki.py | TokenValidator, TokenValidator.refresh, require_auth, wrapper, test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted, test_imports_extracted, test_calls_extracted, test_cache_roundtrip, test_load_defaults, test_save_and_reload, test_partial_toml_uses_defaults, test_sparse_folders_merge_to_parent, test_dense_folder_gets_own_page, test_different_folders_get_separate_groups, test_deep_sparse_merges_upward, test_root_level_files, test_returns_all_files, test_root_files_count_correctly, test_compute_hash_stable, test_empty_manifest_on_missing, test_save_and_reload, test_stale_files_detected, test_fresh_file_not_stale, test_load_manifest_missing_component_ids, test_build_page_contains_symbol, test_build_page_contains_calls, test_build_page_contains_called_by, test_build_page_no_agent_hints, test_build_index_contains_page, test_write_page_creates_file |
## Last Indexed
Commit: d44f14801ddd1ca58358b9c825c4831687dac338 — 2026-04-23