# tests/

## Overview

The tests/ group provides comprehensive regression and contract verification for the core modules: configuration persistence (test_config.py), directory-to-page grouping algorithm (test_grouper.py), file manifest tracking (test_manifest.py), wiki page generation (test_wiki.py), agent CLI commands (test_agent_cli.py), and API contract shape (test_api_contracts.py). It isolates file I/O via TemporaryDirectory and environment variables via _clean_env/_restore_env. End-to-end flows (e.g., test_agent_e2e.py) validate the full pipeline, while specific tests check edge cases like sparse folder merging, partial TOML defaults, and hash stability. This suite catches regressions in both production code and contract adherence (e.g., every tool must have a JSON schema).

## Modules
| File | Purpose |
|------|---------|
| tests/test_agent_e2e.py | End-to-end test for agent error verification flow |
| tests/test_manifest.py |  |
| tests/test_wiki.py |  |
| tests/test_api_contracts.py | API contract tests for agent endpoints and tool schemas |
| tests/test_agent_cli.py | Tests for agent CLI commands and contract outputs |
| tests/test_ast_parser.py | Tests for AST parsing, caching, and node extraction |
| tests/test_config.py |  |
| tests/test_grouper.py |  |
| tests/test_p1_fixes.py | Regression tests for task store, registry, and validation fixes |
| tests/test_agent_context.py | Tests for agent context, indexing, and edit impact analysis |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_config.py::_clean_env` | function |  |
| `tests/test_config.py::_restore_env` | function |  |
| `tests/test_config.py::test_load_defaults` | function |  |
| `tests/test_config.py::test_save_and_reload` | function |  |
| `tests/test_config.py::test_partial_toml_uses_defaults` | function |  |
| `tests/test_grouper.py::test_sparse_folders_merge_to_parent` | function |  |
| `tests/test_grouper.py::test_dense_folder_gets_own_page` | function |  |
| `tests/test_grouper.py::test_different_folders_get_separate_groups` | function |  |
| `tests/test_grouper.py::test_deep_sparse_merges_upward` | function |  |
| `tests/test_grouper.py::test_root_level_files` | function |  |
| `tests/test_grouper.py::test_returns_all_files` | function |  |
| `tests/test_grouper.py::test_root_files_count_correctly` | function |  |
| `tests/test_manifest.py::test_compute_hash_stable` | function |  |
| `tests/test_manifest.py::test_empty_manifest_on_missing` | function |  |
| `tests/test_manifest.py::test_save_and_reload` | function |  |
| `tests/test_manifest.py::test_stale_files_detected` | function |  |
| `tests/test_manifest.py::test_fresh_file_not_stale` | function |  |
| `tests/test_manifest.py::test_load_manifest_missing_component_ids` | function |  |
| `tests/test_wiki.py::_make_node` | function |  |
| `tests/test_wiki.py::test_build_page_contains_symbol` | function |  |
| `tests/test_wiki.py::test_build_page_contains_calls` | function |  |
| `tests/test_wiki.py::test_build_page_contains_called_by` | function |  |
| `tests/test_wiki.py::test_build_page_no_agent_hints` | function |  |
| `tests/test_wiki.py::test_build_index_contains_page` | function |  |
| `tests/test_wiki.py::test_write_page_creates_file` | function |  |
| `tests/test_agent_cli.py::test_agent_capabilities_cli_outputs_contract` | function | Verifies agent capabilities CLI command outputs contract-compliant JSON |
| `tests/test_agent_cli.py::test_agent_schema_cli_outputs_openapi_contract` | function | Verifies agent schema CLI command outputs OpenAPI contract JSON |
| `tests/test_agent_cli.py::test_agent_context_cli_requires_symbol_id` | function | Verifies agent context CLI command rejects missing symbol ID |
| `tests/test_api_contracts.py::test_agent_capabilities_all_tools_have_schemas` | function | Checks every tool in capabilities manifest has a JSON schema |
| `tests/test_api_contracts.py::test_core_tool_contract_top_level_keys` | function | Verifies core tool contract bundles expected top-level keys |
| `tests/test_api_contracts.py::test_agent_capabilities_endpoint_contract` | function | Tests /capabilities endpoint returns valid JSON |
| `tests/test_api_contracts.py::test_agent_schema_endpoint_exports_machine_readable_contract` | function | Tests /schema endpoint returns machine-readable OpenAPI spec |
| `tests/test_api_contracts.py::test_stable_symbol_id_endpoint_contract` | function | Tests /stable-symbol-id endpoint accepts and returns stable IDs |
| `tests/test_api_contracts.py::test_post_edit_verify_endpoint_rejects_oversized_diff` | function | Tests /post-edit-verify rejects diffs exceeding size limit |
| `tests/test_api_contracts.py::test_agent_modules_expose_split_boundaries` | function | Verifies agent modules expose split boundaries in their output |
| `tests/test_api_contracts.py::test_agent_split_modules_own_function_bodies` | function | Verifies split modules own the function bodies they claim |
| `tests/test_agent_e2e.py::test_agent_error_to_verify_flow_on_small_repo` | function | Tests error-to-verify flow on a small repository using cross-reference and post-edit-verify |
| `tests/test_agent_context.py::test_index_status_reports_stale_manifest_entry` | function | Tests index status detects stale manifest entries |
| `tests/test_agent_context.py::test_find_tests_for_symbol_matches_file_and_symbol` | function | Tests find_tests_for_symbol returns matching test file and symbol |
| `tests/test_agent_context.py::test_get_edit_context_includes_source_relations_tests_and_status` | function | Tests get_edit_context includes source relations, tests, and status |
| `tests/test_agent_context.py::test_rest_routes_expose_agent_context_tools` | function | Tests REST routes expose agent context tools by inspecting source |
| `tests/test_agent_context.py::test_mcp_servers_expose_agent_context_tools` | function | Tests MCP servers expose agent context tools by inspecting source |
| `tests/test_agent_context.py::test_resolve_symbol_ranks_exact_name_and_path` | function | Tests resolve_symbol ranks exact name and path matches highest |
| `tests/test_agent_context.py::test_search_symbols_can_explain_hits` | function | Tests search_symbols returns explanations for each hit |
| `tests/test_agent_context.py::test_pre_edit_check_reports_dirty_files_and_test_commands` | function | Tests pre_edit_check reports dirty files and test commands |
| `tests/test_agent_context.py::test_impact_analysis_collects_transitive_relations_tests_and_files` | function | Tests impact_analysis collects transitive relations, tests, and files |
| `tests/test_agent_context.py::test_change_plan_returns_agent_edit_steps_and_commands` | function | Tests change_plan returns agent edit steps and commands |
| `tests/test_agent_context.py::test_diagnose_index_reports_missing_wiki_vector_and_missing_sources` | function | Tests diagnose_index reports missing wiki vector and sources |
| `tests/test_agent_context.py::test_agent_protocol_bundle_is_compact_and_includes_freshness` | function | Tests agent_protocol_bundle is compact and includes freshness info |
| `tests/test_agent_context.py::test_resolve_symbol_uses_natural_language_alias_reasons` | function | Tests resolve_symbol uses natural language alias reasons |
| `tests/test_agent_context.py::test_vector_metadata_marks_entry_points` | function | Tests _build_meta marks entry points in vector metadata |
| `tests/test_agent_context.py::test_list_entry_points_reads_first_class_metadata` | function | Tests list_entry_points reads first-class metadata from manifest |
| `tests/test_agent_context.py::test_locate_from_error_uses_stack_trace_file_and_line` | function | Tests locate_from_error uses stack trace file and line number |
| `tests/test_agent_context.py::test_locate_from_error_matches_http_path_to_entry_point` | function | Tests locate_from_error matches HTTP path to entry point |
| `tests/test_agent_context.py::test_post_edit_verify_maps_diff_to_symbols_tests_and_reindex` | function | Tests post_edit_verify maps diff to symbols, tests, and reindex |
| `tests/test_agent_context.py::test_diff_payload_size_guard_rejects_oversized_diff` | function | Tests _validate_diff_payload rejects oversized diff payloads |
| `tests/test_agent_context.py::test_stable_symbol_id_is_deterministic_and_metadata_includes_it` | function | Tests stable_symbol_id is deterministic and included in metadata |
| `tests/test_agent_context.py::test_change_set_combines_target_impact_tests_and_post_edit` | function | Tests change_set combines target, impact, tests, and post-edit |
| `tests/test_agent_context.py::test_change_set_respects_max_results_and_summary` | function | Tests change_set respects max_results and returns summary |
| `tests/test_agent_context.py::test_coverage_map_links_tests_to_source_symbols` | function | Tests coverage_map links tests to source symbols |
| `tests/test_agent_context.py::test_coverage_map_repo_wide_respects_max_results` | function | Tests coverage_map repo-wide respects max_results |
| `tests/test_agent_context.py::test_index_diff_report_compares_symbol_sets` | function | Tests index_diff_report compares symbol sets between indexes |
| `tests/test_agent_context.py::test_cross_repo_graph_links_client_to_backend_route` | function | Tests cross_repo_graph links client symbol to backend route |
| `tests/test_agent_context.py::test_cross_repo_graph_links_graphql_operation` | function | Tests cross_repo_graph links GraphQL operation symbol |
| `tests/test_agent_context.py::test_cross_repo_graph_respects_max_results` | function | Tests cross_repo_graph respects max_results limit |
| `tests/test_agent_context.py::test_index_diff_report_detects_rename_by_stable_id` | function | Tests index_diff_report detects renames by stable symbol ID |
| `tests/test_agent_context.py::test_agent_capabilities_manifest_lists_local_and_remote_tools` | function | Tests agent_capabilities_manifest lists local and remote tools |
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function | Tests parse_file returns a list of AST nodes |
| `tests/test_ast_parser.py::test_function_node` | function | Tests parse_file extracts function nodes correctly |
| `tests/test_ast_parser.py::test_method_node` | function | Tests parse_file extracts method nodes correctly |
| `tests/test_ast_parser.py::test_class_node` | function | Tests parse_file extracts class nodes correctly |
| `tests/test_ast_parser.py::test_docstring_extracted` | function | Tests parse_file extracts docstring from nodes |
| `tests/test_ast_parser.py::test_imports_extracted` | function | Tests parse_file extracts imports from nodes |
| `tests/test_ast_parser.py::test_calls_extracted` | function | Tests parse_file extracts function calls from nodes |
| `tests/test_ast_parser.py::test_python_fastapi_route_entry_point` | function | Tests parse_file detects FastAPI route entry points |
| `tests/test_ast_parser.py::test_python_click_command_entry_point` | function | Tests parse_file detects Click command entry points |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function | Tests save_cached_nodes and load_cached_nodes round-trip correctly |
| `tests/test_ast_parser.py::test_rust_parse_returns_nodes` | function | Tests Rust file parse_file returns nodes |
| `tests/test_ast_parser.py::test_rust_function_node` | function | Tests Rust file parse_file extracts function nodes |
| `tests/test_ast_parser.py::test_rust_struct_node` | function | Tests Rust file parse_file extracts struct nodes |
| `tests/test_ast_parser.py::test_rust_method_node` | function | Tests Rust file parse_file extracts method nodes |
| `tests/test_ast_parser.py::test_rust_trait_node` | function | Tests Rust file parse_file extracts trait nodes |
| `tests/test_ast_parser.py::test_rust_trait_method_spec` | function | Tests Rust file parse_file extracts trait method specifications |
| `tests/test_ast_parser.py::test_rust_enum_node` | function | Tests Rust file parse_file extracts enum nodes |
| `tests/test_ast_parser.py::test_rust_type_alias` | function | Tests Rust file parse_file extracts type alias nodes |
| `tests/test_ast_parser.py::test_rust_docstring_extracted` | function | Tests Rust file parse_file extracts docstrings |
| `tests/test_ast_parser.py::test_rust_imports_extracted` | function | Tests Rust file parse_file extracts import nodes |
| `tests/test_ast_parser.py::test_java_parse_returns_nodes` | function | Tests Java file parse_file returns nodes |
| `tests/test_ast_parser.py::test_java_class_node` | function | Tests Java file parse_file extracts class nodes |
| `tests/test_ast_parser.py::test_java_method_node` | function | Tests Java file parse_file extracts method nodes |
| `tests/test_ast_parser.py::test_java_interface_node` | function | Tests Java file parse_file extracts interface nodes |
| `tests/test_ast_parser.py::test_java_enum_node` | function | Tests Java file parse_file extracts enum nodes |
| `tests/test_ast_parser.py::test_java_javadoc_extracted` | function | Tests Java file parse_file extracts Javadoc comments |
| `tests/test_ast_parser.py::test_java_imports_extracted` | function | Tests Java file parse_file extracts import statements |
| `tests/test_ast_parser.py::test_ruby_parse_returns_nodes` | function | Tests Ruby file parse_file returns nodes |
| `tests/test_ast_parser.py::test_ruby_class_node` | function | Tests Ruby file parse_file extracts class nodes |
| `tests/test_ast_parser.py::test_ruby_method_node` | function | Tests Ruby file parse_file extracts method nodes |
| `tests/test_ast_parser.py::test_ruby_module_node` | function | Tests Ruby file parse_file extracts module nodes |
| `tests/test_ast_parser.py::test_ruby_function_node` | function | Tests Ruby file parse_file extracts function nodes |
| `tests/test_ast_parser.py::test_ruby_docstring_extracted` | function | Tests Ruby file parse_file extracts docstring comments |
| `tests/test_p1_fixes.py::TestTaskStore` | class | Test suite for TaskStore create, update, get, cleanup |
| `tests/test_p1_fixes.py::TestTaskStore.test_create_task` | method | Tests that create stores a task and get retrieves it |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_task` | method | Tests TaskStore.update updates an existing task's fields |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp` | method | Tests TaskStore.update sets finished timestamp on completion |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop` | method | Tests TaskStore.update does nothing for nonexistent task |
| `tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none` | method | Tests that get returns None for nonexistent task ID |
| `tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks` | method | Tests TaskStore._cleanup removes expired tasks |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety` | class | Tests thread safety of RepoRegistry register/unregister |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register` | method | Tests RepoRegistry.register is thread-safe under concurrent calls |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister` | method | Tests RepoRegistry.unregister is thread-safe under concurrent calls |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock` | class | Test suite for skip-lock mechanism in repo locking |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release` | method | Tests that skip-lock does not release acquired lock |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent` | method | Tests that normal lock blocks concurrent access |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone` | class | Tests get returns None for nonexistent repos |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none` | method | Tests RepoRegistry.get returns None for unregistered repo |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely` | method | Tests RepoRegistry.get returns None safely without error |
| `tests/test_p1_fixes.py::TestParseBody` | class | Tests _parse_body function parsing JSON request body |
| `tests/test_p1_fixes.py::TestParseBody.test_valid_json` | method | Tests _parse_body extracts valid JSON body and returns dict |
| `tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty` | method | Tests _parse_body returns empty dict on invalid JSON |
| `tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty` | method | Tests _parse_body returns empty dict on non-dict JSON |
| `tests/test_p1_fixes.py::asyncio_coro` | function | Returns async coroutine function for mocking |
| `tests/test_p1_fixes.py::TestManifestFieldValidation` | class | Tests manifest field defaults when missing |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty` | method | Tests load_manifest defaults missing component_ids to empty list |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty` | method | Tests load_manifest defaults missing hash to empty string |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty` | method | Tests load_manifest returns empty dict on corrupt JSON |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString` | class | Tests empty env string does not override default config |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default` | method | Tests _apply_env does not override default with empty string |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck` | class | Tests git checkout failure sets task status to failed |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed` | method | Tests _run_rebuild_task_inner marks task failed on git checkout failure |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers` | class | Tests cross-reference merging caller lists across files |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers` | method | Tests cross_reference merges callers from same and different files |
| `tests/test_p1_fixes.py::TestUpdateMetaLock` | class | Tests update_meta uses a lock |
| `tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock` | method | Tests update_meta uses a lock to protect registry metadata |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping` | class | Tests stripping quotes from env file values |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped` | method | Tests load_env_file strips double quotes from environment values |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped` | method | Tests load_env_file strips single quotes from environment values |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList` | class | Tests _truncate_list produces valid JSON |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json` | method | Tests _truncate_list produces valid JSON output |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated` | method | Tests small lists remain unchanged |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion` | class | Tests string params converted to int in get_source_context |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int` | method | Tests get_source_context converts string params to int |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock` | class | Tests unregister removes the repo lock file |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock` | method | Tests RepoRegistry.unregister removes the repo lock file |
| `tests/test_p1_fixes.py::TestAtomicWrites` | class | Tests atomic writes of config and manifest files |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic` | method | Tests save_config writes atomically without corrupting existing config |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic` | method | Tests save_manifest writes atomically without corrupting existing manifest |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause` | class | Tests single branch retrieval using where clause |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause` | method | Tests RepoRegistry generates WHERE clause for single branch |
| `tests/test_p1_fixes.py::TestIntParamValidation` | class | Tests integer param validation returns 400 on invalid |
| `tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400` | method | Tests get_source_context returns 400 on invalid line_start |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy` | class | Tests webhook branch list is not mutated |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy.test_webhook_branch_list_not_mutated` | method | Tests webhook branch list is not mutated by other operations |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning` | class | Tests cleanup does not evict running tasks |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks` | method | Tests _cleanup does not remove tasks with status running |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse` | class | Tests embed_query raises on empty response |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty` | method | Tests embed_query raises exception on empty response from model |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone` | class | Tests compute_hash returns None on OS error |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror` | method | Tests compute_hash returns None on file read error |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit` | class | Tests changed_files_since raises on invalid commit |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit` | method | Tests changed_files_since raises on invalid commit hash |
| `tests/test_p1_fixes.py::TestExpansionCap` | class | Tests _expand_with_call_graph respects max expansion limit |
| `tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max` | method | Tests _expand_with_call_graph caps expansion at max results |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion` | class | Tests expansion caps at max with actual expansions |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max` | method | Tests expansion caps at max even with larger call graph |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape` | class | Tests script tag escaping in API key dumps |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape.test_api_key_script_tag_escaped` | method | Tests API key string escapes HTML script tags |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive` | class | Tests case-insensitive Bearer token parsing |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive.test_lowercase_bearer_accepted` | method | Tests Bearer token comparison is case-insensitive |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK` | class | Tests CJK token estimation uses triple character budget |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple` | method | Tests build_batches uses triple token budget for CJK characters |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock` | class | Tests reentrant lock prevents deadlock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock` | method | Tests RepoRegistry.register does not deadlock with RLock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_rlock_allows_reentrant` | method | Tests reentrant lock allows nested acquires |
| `tests/test_p1_fixes.py::TestTopKNegativeValue` | class | Tests clamping negative top_k values to one |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_negative_clamped_to_one` | method | Tests top_k value clamped to minimum 1 when negative |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_zero_clamped_to_one` | method | Tests top_k value clamped to minimum 1 when zero |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_normal_value` | method | Asserts top_k normal value passes validation using max and min |
| `tests/test_p1_fixes.py::TestEmbeddingRetry` | class | Tests embedding API call has retry logic |
| `tests/test_p1_fixes.py::TestEmbeddingRetry.test_call_embedding_api_has_retry` | method | Tests call_embedding_api includes retry decorator |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection` | class | Tests protection against empty choices from LLM |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection.test_litellm_empty_choices_raises_custom_error` | method | Tests empty choices raises custom error |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes` | class | Tests stale detection uses all node IDs |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes.test_stale_uses_all_node_ids` | method | Tests stale check uses all node IDs in document |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet` | class | Tests branch always present in metadata |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet.test_branch_always_in_metadata` | method | Tests branch field always set in vector store metadata |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd` | class | Tests discover_remote_branches has cwd parameter |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd.test_discover_has_cwd_param` | method | Tests discover_remote_branches accepts a cwd parameter |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite` | class | Tests credential write uses temporary file |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite.test_credential_write_uses_tmp` | method | Tests credential write uses temporary file |
| `tests/test_p1_fixes.py::TestConfigValidation` | class | Tests config validation resets invalid values |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset` | method | Tests config resets invalid max_tokens_per_batch via load and save |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset` | method | Tests config resets invalid dimensions via load and save |
| `tests/test_p1_fixes.py::TestRubyModuleMethod` | class | Tests Ruby module method naming with prefix |
| `tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix` | method | Verifies Ruby module method has prefix in parsed output |
| `tests/test_p1_fixes.py::TestVectorStoreIncrementalSafety` | class | Tests upsert_nodes uses file-scoped stale detection |
| `tests/test_p1_fixes.py::TestVectorStoreIncrementalSafety.test_upsert_nodes_uses_file_scoped_stale` | method | Tests upsert_nodes scopes stale check to file |
| `tests/test_p1_fixes.py::TestDimensionMismatchDetection` | class | Tests dimension mismatch detection when getting collection |
| `tests/test_p1_fixes.py::TestDimensionMismatchDetection.test_get_or_create_checks_dim` | method | Tests get_or_create_collection validates dimensions |
| `tests/test_p1_fixes.py::TestListReposNullSafety` | class | Tests list_repos handles None safely |
| `tests/test_p1_fixes.py::TestListReposNullSafety.test_list_repos_checks_none` | method | Tests list_repos returns empty list when None |
| `tests/test_p1_fixes.py::TestExpandDepthClamped` | class | Tests clamping expansion depth to maximum of 5 |
| `tests/test_p1_fixes.py::TestExpandDepthClamped.test_expand_depth_max_5` | method | Tests expand_depth clamped to max 5 |
| `tests/test_p1_fixes.py::TestWebhookNullCheck` | class | Tests webhook null check on info |
| `tests/test_p1_fixes.py::TestWebhookNullCheck.test_webhook_checks_info_not_none` | method | Tests webhook handler checks info is not None |
| `tests/test_p1_fixes.py::TestURLValidationBeforeDiscovery` | class | Tests URL validation before discovery in register |
| `tests/test_p1_fixes.py::TestURLValidationBeforeDiscovery.test_register_validates_url_before_discovery` | method | Tests register validates URL before remote discovery |
| `tests/test_p1_fixes.py::TestNonGitManifestCleanup` | class | Tests cleaning non-git manifests during update |
| `tests/test_p1_fixes.py::TestNonGitManifestCleanup.test_update_manifest_cleans_non_git` | method | Tests update_manifest removes non-git manifests |
| `tests/test_p1_fixes.py::TestLLMListResponseHandling` | class | Tests deep_enrich_index handles list responses |
| `tests/test_p1_fixes.py::TestLLMListResponseHandling.test_deep_enrich_index_handles_list` | method | Tests deep_enrich_index handles list LLM responses |
| `tests/test_p1_fixes.py::TestSafeIdFunction` | class | Test suite for safe ID function |
| `tests/test_p1_fixes.py::TestSafeIdFunction.test_safeId_exists_in_html` | method |  |
| `tests/test_p1_fixes.py::TestMCPResponseSizeLimit` | class |  |
| `tests/test_p1_fixes.py::TestMCPResponseSizeLimit.test_api_request_limits_response` | method |  |
| `tests/test_p1_fixes.py::TestMergeThresholdValidation` | class |  |
| `tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated` | method | Tests merge threshold validation with config load and save |
| `tests/test_p1_fixes.py::TestVectorStoreLogger` | class |  |
| `tests/test_p1_fixes.py::TestVectorStoreLogger.test_vector_store_has_logger` | method |  |
| `tests/test_p1_fixes.py::TestNonGitCliFileDiscovery` | class |  |
| `tests/test_p1_fixes.py::TestNonGitCliFileDiscovery.test_cli_non_git_uses_rglob` | method |  |
| `tests/test_p1_fixes.py::TestSearchDimNone` | class |  |
| `tests/test_p1_fixes.py::TestSearchDimNone.test_search_passes_dim_none` | method |  |
| `tests/test_p1_fixes.py::TestClientThreadSafety` | class |  |
| `tests/test_p1_fixes.py::TestClientThreadSafety.test_anthropic_client_has_lock` | method |  |
| `tests/test_p1_fixes.py::TestClientThreadSafety.test_embedding_openai_client_has_lock` | method |  |
| `tests/test_p1_fixes.py::TestFatalExceptionsUnified` | class |  |
| `tests/test_p1_fixes.py::TestFatalExceptionsUnified.test_fatal_exceptions_constant` | method |  |
| `tests/test_p1_fixes.py::TestMCPExpandDepthClamped` | class |  |
| `tests/test_p1_fixes.py::TestMCPExpandDepthClamped.test_mcp_expand_depth_max_5` | method |  |
| `tests/test_p1_fixes.py::TestDefaultBranchDetection` | class |  |
| `tests/test_p1_fixes.py::TestDefaultBranchDetection.test_register_task_detects_default_branch` | method |  |
| `tests/test_p1_fixes.py::TestAPIKeyNotInHTML` | class |  |
| `tests/test_p1_fixes.py::TestAPIKeyNotInHTML.test_api_key_not_embedded_in_page` | method |  |
| `tests/test_p1_fixes.py::TestBranchFilterConsistent` | class |  |
| `tests/test_p1_fixes.py::TestBranchFilterConsistent.test_retrieval_always_filters_by_branch` | method |  |
| `tests/test_p1_fixes.py::TestLoadReposHasCatch` | class |  |
| `tests/test_p1_fixes.py::TestLoadReposHasCatch.test_loadrepos_has_catch` | method | Verifies load_repos includes exception handling in source code |
| `tests/test_p1_fixes.py::TestAnthropicImport` | class |  |
| `tests/test_p1_fixes.py::TestAnthropicImport.test_anthropic_imported_in_completion` | method |  |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions` | class |  |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions.test_retry_uses_fatal_exceptions_constant` | method | Asserts retry function references FATAL_EXCEPTIONS constant in source |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone` | class |  |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone.test_delete_by_files_passes_dim_none` | method |  |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid` | class |  |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid.test_all_new_ids_uses_valid_only` | method |  |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch` | class |  |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch.test_openrepo_has_catch` | method | Verifies open_repo includes exception handling in source code |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch` | class |  |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch.test_dosearch_has_catch` | method | Verifies do_search includes exception handling in source code |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped` | class |  |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped.test_trace_call_max_depth_clamped` | method |  |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound` | class |  |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound.test_trace_call_max_depth_lower_bound` | method |  |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation` | class |  |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation.test_tags_type_validation` | method |  |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy` | class |  |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy.test_build_batches_includes_called_by` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes` | class |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_ls_remote` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_store_credentials` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_expand_depth_lower_bound` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_url_empty_check_before_discovery` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_no_duplicate_url_validation` | method | Verifies no duplicate URL validation call in source using count |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_git_add_timeout` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_warnings_warn` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_unused_imports` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_unused_config_imports` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_mcp_no_unused_socket_import` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_max_depth_limit_consistent` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_retrieval_branch_empty_means_no_filter` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_uses_retrieval_trace_call` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_duplicate_parse_json_list` | method | Asserts no duplicate parse_json_list call in REST API source |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_description_type_validation` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_tags_element_type_validation` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes` | class | Test suite for round 15 fixes: exception handling and syntax |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_manifest` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_wiki_pages` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_api_json_parse_error_handling` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_sync_branch_has_try_catch` | method | Verifies sync_branch includes try-except in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_rebuild_branch_has_try_catch` | method | Verifies rebuild_branch includes try-except in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_register_missing_branch_has_try_catch` | method | Verifies register_missing_branch includes try-except in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_edit_meta_polls_reindex_task` | method | Verifies edit_meta calls reindex_task in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_unregister_has_try_catch` | method | Verifies do_unregister includes try-except in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_validate_has_try_catch` | method | Verifies do_validate includes try-except in source code |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_querySelector_title_optional_chaining` | method | Asserts querySelector title uses optional chaining in source |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_assert_operator_precedence_fixed` | method | Verifies operator precedence is corrected in assert statement |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_no_duplicate_anthropic_lock_test` | method | Asserts no duplicate anthropic lock test call in source |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_indexer_toml_no_dashscope_hardcoded` | method | Verifies indexer.toml avoids hardcoded dashscope via string inspection |
| `tests/test_p1_fixes.py::TestRound16Fixes` | class | Test suite for round 16 fixes: indexing, cleanup, and eviction |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_reindex_allows_index_only_request` | method | Tests reindex endpoint accepts index-only request via POST |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_reindex_uses_shared_all_branches_runner` | method | Verifies reindex uses shared all_branches_runner via source inspection |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_destructive_git_cleanup_before_checkout` | method | Tests destructive git cleanup occurs before checkout using mocks |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_rebuild_git_before_delete` | method | Verifies rebuild occurs before git delete in source order |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_branch_detection_after_clone` | method | Asserts branch detection occurs after clone in source |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_upsert_before_manifest` | method | Verifies vector upsert occurs before manifest generation |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_progress_offset_in_pipeline` | method | Checks progress offset is present in pipeline source |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_sync_repo_url_initialized_before_try` | method | Verifies sync_repo URL initialized before try block |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_clone_dir_cleanup_on_failure` | method | Asserts clone directory cleanup on failure using source count |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_eviction` | method | Verifies vector_store_client eviction is callable |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_lock` | method | Checks vector_store_client lock is present in source |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_empty_branches_to_index_check` | method | Verifies empty branches to index list is handled |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_timeout_expired_includes_cmd` | method | Asserts timeout expired handler includes cmd parameter |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_skill_metadata_not_zero` | method | Verifies skill metadata does not contain zero values |
| `tests/test_p1_fixes.py::TestRound17Fixes` | class | Test suite for round 17 fixes: coercion and git config |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_register_task_no_undefined_description_tags` | method | Verifies register_task has no undefined description tags |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_unregister_uses_root_not_path` | method | Asserts unregister uses root not path parameter |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_search_symbols_int_coercion` | method | Verifies search_symbols coerces inputs to integer |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_trace_call_int_coercion` | method | Verifies trace_call coerces inputs to integer |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_git_config_has_timeout` | method | Checks git config function includes timeout parameter |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_detect_default_branch_has_git_terminal_prompt` | method | Verifies detect_default_branch uses GitTerminalPrompt |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_rebuild_evicts_vector_client_before_rmtree` | method | Asserts rebuild evicts vector client before rmtree |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_api_parses_json_error_body` | method | Verifies API parses JSON error body correctly |
| `tests/test_p1_fixes.py::TestRound18Fixes` | class | Test suite for round 18 fixes: timeout handlers and prompts |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_rebuild_has_timeout_expired_handler` | method | Verifies rebuild includes timeout expired handler |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_py_has_git_terminal_prompt` | method | Asserts git.py uses GitTerminalPrompt in source |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_cli_git_add_has_git_terminal_prompt` | method | Verifies CLI git add uses GitTerminalPrompt in source |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_step_names_includes_git_steps` | method | Checks step names include git steps in source |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_evict_client_logs_on_failure` | method | Verifies evict client logs on failure in source |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_reset_return_code_checked` | method | Asserts git reset return code is checked in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations` | class | Test suite for performance optimizations: caching and parallelism |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_description_cache_functions_exist` | method | Verifies description cache functions are callable |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_file_description_cache_functions_exist` | method | Verifies file description cache functions are callable |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_description_cache` | method | Verifies pipeline uses description cache in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_file_description_cache` | method | Verifies pipeline uses file description cache in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_batch_size_increased` | method | Asserts embedding batch size increased in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_describe_files_parallel` | method | Verifies describe_files uses parallelism in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parse_candidates_parallel` | method | Verifies parse_candidates uses parallelism in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_vector_store_batch_query` | method | Verifies vector store batch query is used in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_cache_functions_exist` | method | Verifies embedding cache functions are callable |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_upsert_vectors_uses_embedding_cache` | method | Verifies upsert_vectors uses embedding cache in source |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parallel_symbol_and_file_description` | method | Verifies parallel processing for symbol and file descriptions |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_write_wiki_pages_accepts_precomputed_groups` | method | Asserts write_wiki_pages accepts precomputed groups parameter |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_load_existing_nodes_uses_manifest_hash` | method | Verifies load_existing_nodes uses manifest hash in source |
| `tests/test_p1_fixes.py::_coro` | function |  |
| `tests/test_p1_fixes.py::run` | function | Tests using get_source_context and patch for source analysis |
| `tests/test_p1_fixes.py::run` | function | Tests using get_source_context and patch for source analysis |
| `tests/test_p1_fixes.py::run` | function | Tests using get_source_context and patch for source analysis |
| `tests/test_p1_fixes.py::run` | function | Tests using get_source_context and patch for source analysis |
| `tests/test_p1_fixes.py::run` | function | Tests using get_source_context and patch for source analysis |
| `tests/test_p1_fixes.py::register_repo` | function | Registers a test repository using Path and register helper |
| `tests/test_p1_fixes.py::unregister_repo` | function | Unregisters a test repository using unregister helper |
## Data Flows
- test_config::test_save_and_reload → create Config, save to TOML, reload, assert equality
- test_grouper::test_sparse_folders_merge_to_parent → build directory tree, call density_group, verify file groups merged upward
- test_manifest::test_save_and_reload → create Manifest + FileEntry, save to JSON, reload, assert contents match
- test_wiki::test_build_page_contains_symbol → mock ASTNode, create PageContext, call build_page, verify symbol in output
- test_agent_cli::test_agent_capabilities_cli_outputs_contract → invoke CLI via CliRunner, parse JSON, validate contract fields
- test_api_contracts::test_core_tool_contract_top_level_keys → load Config, setattr to simulate full bundle, assert expected keys exist
## Design Constraints
- test_config functions use _clean_env/_restore_env to pop/restore specific env vars; they must be called in that order and are not idempotent if called outside test flow
- density_group expects input as list of (Path, file_count) tuples; hierarchy is determined by Path.relative_to and parent anchor logic; sparse means <=1 file per folder
- test_manifest hash test uses NamedTemporaryFile with delete=False; file remains until test ends; compute_hash reads entire file content
- test_api_contracts modifies Config attributes via setattr to create a synthetic agent_protocol_bundle; this mutates the global Config object and is not thread-safe
- test_wiki _make_node returns ASTNode with 'calls' and 'called_by' as lists; the symbols must be added via update() afterwards
- test_agent_cli uses CliRunner from click.testing; each test invokes a separate Click command group; output is captured as string and parsed with json.loads
## Relationships
- **Calls:** ASTNode, CliRunner, Config, EmbeddingConfig, Exception, FileEntry, IndexEntry, MagicMock, Manifest, Mock, NamedTemporaryFile, PageContext, Path, RLock, RepoRegistry, TaskStore, TemporaryDirectory, TestClient, Thread, __import__, _apply_env, _build_meta, _clean_env, _cleanup, _coro, _expand_with_call_graph, _get_repo_lock, _make_node, _parse_body, _restore_env, _run_rebuild_task_inner, _truncate_list, _validate_diff_payload, acquire, agent_capabilities_manifest, agent_protocol_bundle, all, any, append, asyncio_coro, build_batches, build_index, build_page, callable, change_plan, change_set, changed_files_since, compare_digest, compute_hash, count, coverage_map, create, create_app, cross_reference, cross_repo_graph, density_group, diagnose_index, dict, dumps, embed_query, endswith, enumerate, exists, extend, find, find_tests_for_symbol, get, get_edit_context, get_index_status, get_source_context, getsource, getsourcefile, git_fetch_checkout_pull, hasattr, impact_analysis, index, index_diff_report, invoke, isinstance, items, join, json, keys, len, list, list_entry_points, load_cached_nodes, load_config, load_env_file, load_manifest, loads, locate_from_error, lower, max, min, mkdir, mkdtemp, next, object, open, parse_file, parse_ruby_file, patch, pop, post, post_edit_verify, pre_edit_check, range, read, read_text, register, release, replace, resolve_symbol, rfind, run, save_cached_nodes, save_config, save_manifest, search_symbols, set, setattr, signature, split, splitlines, stable_symbol_id, stale_files, start, startswith, str, strip, time, unregister, update, update_meta, values, write, write_bytes, write_page, write_text
- **Called by:** indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/git.py::_run, indexer/git.py::_run_checked, indexer/git_ops.py::_cleanup_worktree, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::list_repos, indexer/rest_api.py::repo_detail, indexer/retrieval.py::_git_diff, indexer/retrieval.py::_git_dirty_files, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::asyncio_coro, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** asyncio, click.testing.CliRunner, hmac, indexer.agent_context, indexer.agent_diagnostics, indexer.agent_diff, indexer.agent_graph, indexer.agent_protocol, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.cli.main, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config._apply_env, indexer.config.load_config, indexer.config.save_config, indexer.embedding._call_embedding_api, indexer.embedding._get_openai_client, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_query, indexer.git.changed_files_since, indexer.git_ops.GitOperationError, indexer.git_ops._detect_default_branch, indexer.git_ops.git_fetch_checkout_pull, indexer.grouper.density_group, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_embeddings, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.prepare_descriptions, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_embeddings, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_wiki_pages, indexer.llm._anthropic_completion, indexer.llm._get_anthropic_client, indexer.llm._litellm_completion, indexer.llm.deep_enrich_index, indexer.llm.describe_files, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server, indexer.rest_api, indexer.rest_api.RepoRegistry, indexer.rest_api.TaskStore, indexer.rest_api._InvalidBodyError, indexer.rest_api._discover_remote_branches, indexer.rest_api._get_repo_lock, indexer.rest_api._index_page, indexer.rest_api._locks_lock, indexer.rest_api._parse_body, indexer.rest_api._repo_locks, indexer.rest_api._run_indexing_pipeline, indexer.rest_api._run_rebuild_task_inner, indexer.rest_api._run_register_task_inner, indexer.rest_api._run_sync_task, indexer.rest_api._store_credentials, indexer.rest_api.create_app, indexer.rest_api.get_source_context, indexer.rest_api.list_repos, indexer.rest_api.register_repo, indexer.rest_api.reindex_repo, indexer.rest_api.search_symbols, indexer.rest_api.tasks, indexer.rest_api.trace_call, indexer.rest_api.webhook_by_name, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.agent_capabilities_manifest, indexer.retrieval.agent_protocol_bundle, indexer.retrieval.change_plan, indexer.retrieval.change_set, indexer.retrieval.coverage_map, indexer.retrieval.cross_repo_graph, indexer.retrieval.diagnose_index, indexer.retrieval.find_tests_for_symbol, indexer.retrieval.get_edit_context, indexer.retrieval.get_index_status, indexer.retrieval.impact_analysis, indexer.retrieval.index_diff_report, indexer.retrieval.list_entry_points, indexer.retrieval.locate_from_error, indexer.retrieval.post_edit_verify, indexer.retrieval.pre_edit_check, indexer.retrieval.resolve_symbol, indexer.retrieval.search_symbols, indexer.retrieval.stable_symbol_id, indexer.ruby_parser.parse_ruby_file, indexer.utils, indexer.utils.FATAL_EXCEPTIONS, indexer.utils._env_loaded, indexer.utils.load_env_file, indexer.vector_store, indexer.vector_store._build_meta, indexer.vector_store._get_client, indexer.vector_store._get_or_create_collection, indexer.vector_store._truncate_list, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, inspect, json, os, pathlib.Path, starlette.testclient.TestClient, subprocess, tempfile, threading, time, unittest.mock.MagicMock, unittest.mock.Mock, unittest.mock.patch
## Entry Points
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
- `test_agent_capabilities_cli_outputs_contract`
- `test_agent_schema_cli_outputs_openapi_contract`
- `test_agent_context_cli_requires_symbol_id`
- `test_agent_capabilities_all_tools_have_schemas`
- `test_core_tool_contract_top_level_keys`
- `test_agent_capabilities_endpoint_contract`
- `test_agent_schema_endpoint_exports_machine_readable_contract`
- `test_stable_symbol_id_endpoint_contract`
- `test_post_edit_verify_endpoint_rejects_oversized_diff`
- `test_agent_modules_expose_split_boundaries`
- `test_agent_split_modules_own_function_bodies`
- `test_agent_error_to_verify_flow_on_small_repo`
- `test_index_status_reports_stale_manifest_entry`
- `test_find_tests_for_symbol_matches_file_and_symbol`
- `test_get_edit_context_includes_source_relations_tests_and_status`
- `test_rest_routes_expose_agent_context_tools`
- `test_mcp_servers_expose_agent_context_tools`
- `test_resolve_symbol_ranks_exact_name_and_path`
- `test_search_symbols_can_explain_hits`
- `test_pre_edit_check_reports_dirty_files_and_test_commands`
- `test_impact_analysis_collects_transitive_relations_tests_and_files`
- `test_change_plan_returns_agent_edit_steps_and_commands`
- `test_diagnose_index_reports_missing_wiki_vector_and_missing_sources`
- `test_agent_protocol_bundle_is_compact_and_includes_freshness`
- `test_resolve_symbol_uses_natural_language_alias_reasons`
- `test_vector_metadata_marks_entry_points`
- `test_list_entry_points_reads_first_class_metadata`
- `test_locate_from_error_uses_stack_trace_file_and_line`
- `test_locate_from_error_matches_http_path_to_entry_point`
- `test_post_edit_verify_maps_diff_to_symbols_tests_and_reindex`
- `test_diff_payload_size_guard_rejects_oversized_diff`
- `test_stable_symbol_id_is_deterministic_and_metadata_includes_it`
- `test_change_set_combines_target_impact_tests_and_post_edit`
- `test_change_set_respects_max_results_and_summary`
- `test_coverage_map_links_tests_to_source_symbols`
- `test_coverage_map_repo_wide_respects_max_results`
- `test_index_diff_report_compares_symbol_sets`
- `test_cross_repo_graph_links_client_to_backend_route`
- `test_cross_repo_graph_links_graphql_operation`
- `test_cross_repo_graph_respects_max_results`
- `test_index_diff_report_detects_rename_by_stable_id`
- `test_agent_capabilities_manifest_lists_local_and_remote_tools`
- `test_parse_returns_nodes`
- `test_function_node`
- `test_method_node`
- `test_class_node`
- `test_docstring_extracted`
- `test_imports_extracted`
- `test_calls_extracted`
- `test_python_fastapi_route_entry_point`
- `test_python_click_command_entry_point`
- `test_cache_roundtrip`
- `test_rust_parse_returns_nodes`
- `test_rust_function_node`
- `test_rust_struct_node`
- `test_rust_method_node`
- `test_rust_trait_node`
- `test_rust_trait_method_spec`
- `test_rust_enum_node`
- `test_rust_type_alias`
- `test_rust_docstring_extracted`
- `test_rust_imports_extracted`
- `test_java_parse_returns_nodes`
- `test_java_class_node`
- `test_java_method_node`
- `test_java_interface_node`
- `test_java_enum_node`
- `test_java_javadoc_extracted`
- `test_java_imports_extracted`
- `test_ruby_parse_returns_nodes`
- `test_ruby_class_node`
- `test_ruby_method_node`
- `test_ruby_module_node`
- `test_ruby_function_node`
- `test_ruby_docstring_extracted`
- `TestTaskStore`
- `TestRepoRegistryThreadSafety`
- `TestRepoLockSkipLock`
- `TestRepoRegistryGetNone`
- `TestParseBody`
- `TestManifestFieldValidation`
- `TestApplyEnvEmptyString`
- `TestGitReturnCodeCheck`
- `TestCrossReferenceMergeCallers`
- `TestUpdateMetaLock`
- `TestEnvQuoteStripping`
- `TestVectorStoreTruncateList`
- `TestGetSourceContextTypeCoercion`
- `TestUnregisterCleansLock`
- `TestAtomicWrites`
- `TestSingleBranchWhereClause`
- `TestIntParamValidation`
- `TestWebhookBranchCopy`
- `TestCleanupSkipsRunning`
- `TestEmbedQueryEmptyResponse`
- `TestComputeHashReturnsNone`
- `TestChangedFilesSinceInvalidCommit`
- `TestExpansionCap`
- `TestExpansionCapWithExpansion`
- `TestXSSApiKeyEscape`
- `TestBearerCaseInsensitive`
- `TestBatchTokenEstimateCJK`
- `TestRLockNoDeadlock`
- `TestTopKNegativeValue`
- `TestEmbeddingRetry`
- `TestEmptyChoicesProtection`
- `TestVectorStoreStaleByAllNodes`
- `TestVectorStoreBranchAlwaysSet`
- `TestDiscoverRemoteBranchesCwd`
- `TestCredentialAtomicWrite`
- `TestConfigValidation`
- `TestRubyModuleMethod`
- `TestVectorStoreIncrementalSafety`
- `TestDimensionMismatchDetection`
- `TestListReposNullSafety`
- `TestExpandDepthClamped`
- `TestWebhookNullCheck`
- `TestURLValidationBeforeDiscovery`
- `TestNonGitManifestCleanup`
- `TestLLMListResponseHandling`
- `TestSafeIdFunction`
- `TestMCPResponseSizeLimit`
- `TestMergeThresholdValidation`
- `TestVectorStoreLogger`
- `TestNonGitCliFileDiscovery`
- `TestSearchDimNone`
- `TestClientThreadSafety`
- `TestFatalExceptionsUnified`
- `TestMCPExpandDepthClamped`
- `TestDefaultBranchDetection`
- `TestAPIKeyNotInHTML`
- `TestBranchFilterConsistent`
- `TestLoadReposHasCatch`
- `TestAnthropicImport`
- `TestRetryFatalExceptions`
- `TestDeleteByFilesDimNone`
- `TestAllNewIdsOnlyValid`
- `TestOpenRepoHasCatch`
- `TestDoSearchHasCatch`
- `TestMCPMaxDepthClamped`
- `TestTraceCallMaxDepthLowerBound`
- `TestTagsBranchesTypeValidation`
- `TestBuildBatchesIncludesCalledBy`
- `TestRound14Fixes`
- `TestRound15Fixes`
- `TestRound16Fixes`
- `TestRound17Fixes`
- `TestRound18Fixes`
- `TestPerformanceOptimizations`
- `register_repo`
- `unregister_repo`
