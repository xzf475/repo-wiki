# tests/

## Overview

The test suite validates the core analytical pipeline: AST parsing (Python, Rust, Java, Ruby), caching, configuration, file grouping, manifest parsing, and wiki generation. Key classes tested include parse_file (multi-language), Config, Grouper, Manifest, and WikiBuilder, ensuring correct symbol extraction, cross-referencing, and output formatting across languages. This guarantees that the system's primary function—automated code analysis and documentation—is robust against regressions and edge cases.

## Modules
| File | Purpose |
|------|---------|
| tests/test_wiki.py |  |
| tests/test_ast_parser.py |  |
| tests/test_config.py |  |
| tests/test_p1_fixes.py |  |
| tests/test_grouper.py |  |
| tests/test_manifest.py |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function |  |
| `tests/test_ast_parser.py::test_function_node` | function |  |
| `tests/test_ast_parser.py::test_method_node` | function |  |
| `tests/test_ast_parser.py::test_class_node` | function |  |
| `tests/test_ast_parser.py::test_docstring_extracted` | function |  |
| `tests/test_ast_parser.py::test_imports_extracted` | function |  |
| `tests/test_ast_parser.py::test_calls_extracted` | function |  |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function |  |
| `tests/test_ast_parser.py::test_rust_parse_returns_nodes` | function |  |
| `tests/test_ast_parser.py::test_rust_function_node` | function |  |
| `tests/test_ast_parser.py::test_rust_struct_node` | function |  |
| `tests/test_ast_parser.py::test_rust_method_node` | function |  |
| `tests/test_ast_parser.py::test_rust_trait_node` | function |  |
| `tests/test_ast_parser.py::test_rust_trait_method_spec` | function |  |
| `tests/test_ast_parser.py::test_rust_enum_node` | function |  |
| `tests/test_ast_parser.py::test_rust_type_alias` | function |  |
| `tests/test_ast_parser.py::test_rust_docstring_extracted` | function |  |
| `tests/test_ast_parser.py::test_rust_imports_extracted` | function |  |
| `tests/test_ast_parser.py::test_java_parse_returns_nodes` | function |  |
| `tests/test_ast_parser.py::test_java_class_node` | function |  |
| `tests/test_ast_parser.py::test_java_method_node` | function |  |
| `tests/test_ast_parser.py::test_java_interface_node` | function |  |
| `tests/test_ast_parser.py::test_java_enum_node` | function |  |
| `tests/test_ast_parser.py::test_java_javadoc_extracted` | function |  |
| `tests/test_ast_parser.py::test_java_imports_extracted` | function |  |
| `tests/test_ast_parser.py::test_ruby_parse_returns_nodes` | function |  |
| `tests/test_ast_parser.py::test_ruby_class_node` | function |  |
| `tests/test_ast_parser.py::test_ruby_method_node` | function |  |
| `tests/test_ast_parser.py::test_ruby_module_node` | function |  |
| `tests/test_ast_parser.py::test_ruby_function_node` | function |  |
| `tests/test_ast_parser.py::test_ruby_docstring_extracted` | function |  |
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
| `tests/test_p1_fixes.py::TestTaskStore` | class |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_create_task` | method |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_task` | method |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp` | method |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop` | method |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none` | method |  |
| `tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks` | method |  |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety` | class |  |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register` | method |  |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister` | method |  |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock` | class |  |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release` | method |  |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent` | method |  |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone` | class |  |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none` | method |  |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely` | method |  |
| `tests/test_p1_fixes.py::TestParseBody` | class |  |
| `tests/test_p1_fixes.py::TestParseBody.test_valid_json` | method |  |
| `tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty` | method |  |
| `tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty` | method |  |
| `tests/test_p1_fixes.py::asyncio_coro` | function |  |
| `tests/test_p1_fixes.py::TestManifestFieldValidation` | class |  |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty` | method |  |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty` | method |  |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty` | method |  |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString` | class |  |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default` | method |  |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck` | class |  |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed` | method |  |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers` | class |  |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers` | method |  |
| `tests/test_p1_fixes.py::TestUpdateMetaLock` | class |  |
| `tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock` | method |  |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping` | class |  |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped` | method |  |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped` | method |  |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList` | class |  |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json` | method |  |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated` | method |  |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion` | class |  |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int` | method |  |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock` | class |  |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock` | method |  |
| `tests/test_p1_fixes.py::TestAtomicWrites` | class |  |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic` | method |  |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic` | method |  |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause` | class |  |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause` | method |  |
| `tests/test_p1_fixes.py::TestIntParamValidation` | class |  |
| `tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400` | method |  |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy` | class |  |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy.test_webhook_branch_list_not_mutated` | method |  |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning` | class |  |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks` | method |  |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse` | class |  |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty` | method |  |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone` | class |  |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror` | method |  |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit` | class |  |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit` | method |  |
| `tests/test_p1_fixes.py::TestExpansionCap` | class |  |
| `tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max` | method |  |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion` | class |  |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max` | method |  |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape` | class |  |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape.test_api_key_script_tag_escaped` | method |  |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive` | class |  |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive.test_lowercase_bearer_accepted` | method |  |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK` | class |  |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple` | method |  |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock` | class |  |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock` | method |  |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_rlock_allows_reentrant` | method |  |
| `tests/test_p1_fixes.py::TestTopKNegativeValue` | class |  |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_negative_clamped_to_one` | method |  |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_zero_clamped_to_one` | method |  |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_normal_value` | method |  |
| `tests/test_p1_fixes.py::TestEmbeddingRetry` | class |  |
| `tests/test_p1_fixes.py::TestEmbeddingRetry.test_call_embedding_api_has_retry` | method |  |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection` | class |  |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection.test_litellm_empty_choices_raises_custom_error` | method |  |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes` | class |  |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes.test_stale_uses_all_node_ids` | method |  |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet` | class |  |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet.test_branch_always_in_metadata` | method |  |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd` | class |  |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd.test_discover_has_cwd_param` | method |  |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite` | class |  |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite.test_credential_write_uses_tmp` | method |  |
| `tests/test_p1_fixes.py::TestConfigValidation` | class |  |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset` | method |  |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset` | method |  |
| `tests/test_p1_fixes.py::TestRubyModuleMethod` | class |  |
| `tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix` | method |  |
| `tests/test_p1_fixes.py::TestVectorStoreIncrementalSafety` | class |  |
| `tests/test_p1_fixes.py::TestVectorStoreIncrementalSafety.test_upsert_nodes_uses_file_scoped_stale` | method |  |
| `tests/test_p1_fixes.py::TestDimensionMismatchDetection` | class |  |
| `tests/test_p1_fixes.py::TestDimensionMismatchDetection.test_get_or_create_checks_dim` | method |  |
| `tests/test_p1_fixes.py::TestListReposNullSafety` | class |  |
| `tests/test_p1_fixes.py::TestListReposNullSafety.test_list_repos_checks_none` | method |  |
| `tests/test_p1_fixes.py::TestExpandDepthClamped` | class |  |
| `tests/test_p1_fixes.py::TestExpandDepthClamped.test_expand_depth_max_5` | method |  |
| `tests/test_p1_fixes.py::TestWebhookNullCheck` | class |  |
| `tests/test_p1_fixes.py::TestWebhookNullCheck.test_webhook_checks_info_not_none` | method |  |
| `tests/test_p1_fixes.py::TestURLValidationBeforeDiscovery` | class |  |
| `tests/test_p1_fixes.py::TestURLValidationBeforeDiscovery.test_register_validates_url_before_discovery` | method |  |
| `tests/test_p1_fixes.py::TestNonGitManifestCleanup` | class |  |
| `tests/test_p1_fixes.py::TestNonGitManifestCleanup.test_update_manifest_cleans_non_git` | method |  |
| `tests/test_p1_fixes.py::TestLLMListResponseHandling` | class |  |
| `tests/test_p1_fixes.py::TestLLMListResponseHandling.test_deep_enrich_index_handles_list` | method |  |
| `tests/test_p1_fixes.py::TestSafeIdFunction` | class |  |
| `tests/test_p1_fixes.py::TestSafeIdFunction.test_safeId_exists_in_html` | method |  |
| `tests/test_p1_fixes.py::TestMCPResponseSizeLimit` | class |  |
| `tests/test_p1_fixes.py::TestMCPResponseSizeLimit.test_api_request_limits_response` | method |  |
| `tests/test_p1_fixes.py::TestMergeThresholdValidation` | class |  |
| `tests/test_p1_fixes.py::TestMergeThresholdValidation.test_merge_threshold_validated` | method |  |
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
| `tests/test_p1_fixes.py::TestLoadReposHasCatch.test_loadrepos_has_catch` | method |  |
| `tests/test_p1_fixes.py::TestAnthropicImport` | class |  |
| `tests/test_p1_fixes.py::TestAnthropicImport.test_anthropic_imported_in_completion` | method |  |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions` | class |  |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions.test_retry_uses_fatal_exceptions_constant` | method |  |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone` | class |  |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone.test_delete_by_files_passes_dim_none` | method |  |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid` | class |  |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid.test_all_new_ids_uses_valid_only` | method |  |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch` | class |  |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch.test_openrepo_has_catch` | method |  |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch` | class |  |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch.test_dosearch_has_catch` | method |  |
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
| `tests/test_p1_fixes.py::TestRound14Fixes.test_no_duplicate_url_validation` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_git_add_timeout` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_warnings_warn` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_unused_imports` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_unused_config_imports` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_mcp_no_unused_socket_import` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_max_depth_limit_consistent` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_retrieval_branch_empty_means_no_filter` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_uses_retrieval_trace_call` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_duplicate_parse_json_list` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_description_type_validation` | method |  |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_tags_element_type_validation` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes` | class |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_manifest` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_wiki_pages` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_api_json_parse_error_handling` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_sync_branch_has_try_catch` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_rebuild_branch_has_try_catch` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_register_missing_branch_has_try_catch` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_unregister_has_try_catch` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_validate_has_try_catch` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_querySelector_title_optional_chaining` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_assert_operator_precedence_fixed` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_no_duplicate_anthropic_lock_test` | method |  |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_indexer_toml_no_dashscope_hardcoded` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes` | class |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_rebuild_git_before_delete` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_branch_detection_after_clone` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_upsert_before_manifest` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_progress_offset_in_pipeline` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_sync_repo_url_initialized_before_try` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_clone_dir_cleanup_on_failure` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_eviction` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_lock` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_empty_branches_to_index_check` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_timeout_expired_includes_cmd` | method |  |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_skill_metadata_not_zero` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes` | class |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_register_task_no_undefined_description_tags` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_unregister_uses_root_not_path` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_search_symbols_int_coercion` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_trace_call_int_coercion` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_git_config_has_timeout` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_detect_default_branch_has_git_terminal_prompt` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_rebuild_evicts_vector_client_before_rmtree` | method |  |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_api_parses_json_error_body` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes` | class |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_rebuild_has_timeout_expired_handler` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_py_has_git_terminal_prompt` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_cli_git_add_has_git_terminal_prompt` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_step_names_includes_git_steps` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_evict_client_logs_on_failure` | method |  |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_reset_return_code_checked` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations` | class |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_description_cache_functions_exist` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_file_description_cache_functions_exist` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_description_cache` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_file_description_cache` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_batch_size_increased` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_describe_files_parallel` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parse_candidates_parallel` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_vector_store_batch_query` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_cache_functions_exist` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_upsert_vectors_uses_embedding_cache` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parallel_symbol_and_file_description` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_write_wiki_pages_accepts_precomputed_groups` | method |  |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_load_existing_nodes_uses_manifest_hash` | method |  |
| `tests/test_p1_fixes.py::_coro` | function |  |
| `tests/test_p1_fixes.py::run` | function |  |
| `tests/test_p1_fixes.py::run` | function |  |
| `tests/test_p1_fixes.py::run` | function |  |
| `tests/test_p1_fixes.py::run` | function |  |
| `tests/test_p1_fixes.py::run` | function |  |
| `tests/test_p1_fixes.py::register_repo` | function |  |
| `tests/test_p1_fixes.py::unregister_repo` | function |  |
## Data Flows
- Parser tests: sample source string → parse_file() → assert node count, type, name, docstring, imports, calls.
- Cache tests: parse_file() → save_cached_nodes() → load_cached_nodes() → verify roundtrip equality and length.
- Grouper tests: mock manifest entries → Grouper.group() → check output groupings (by language, directory, custom rules).
- Wiki tests: mock manifest + parsed nodes → WikiBuilder.generate() → assert file existence, section headers, and cross-links.
## Design Constraints
- All parser tests use inline source strings or TemporaryDirectory—no external file dependencies to ensure isolation and speed.
- Java/Ruby parser tests require tree-sitter parsers; they must skip (not fail) via pytest marks if parsers are missing.
- Cache tests must clean up serialized files after each run to avoid cross-test contamination.
- test_p1_fixes are regression tests; they are expected to fail if the corresponding bug fix is accidentally reverted.
- Manifest tests raise ValueError on empty or malformed input; the Config test ensures missing keys fall back to defaults without crashing.
- Wiki tests generate output into a temporary directory that is recreated before each test to guarantee a clean slate.
## Relationships
- **Calls:** ASTNode, Config, EmbeddingConfig, Exception, FileEntry, IndexEntry, MagicMock, Manifest, NamedTemporaryFile, PageContext, Path, RLock, RepoRegistry, TaskStore, TemporaryDirectory, Thread, __import__, _apply_env, _clean_env, _cleanup, _coro, _expand_with_call_graph, _get_repo_lock, _make_node, _parse_body, _restore_env, _run_rebuild_task_inner, _truncate_list, acquire, all, any, append, asyncio_coro, build_batches, build_index, build_page, callable, changed_files_since, compare_digest, compute_hash, count, create, cross_reference, density_group, dict, dumps, embed_query, endswith, exists, find, get, get_source_context, getsource, hasattr, index, isinstance, items, join, keys, len, list, load_cached_nodes, load_config, load_env_file, load_manifest, loads, lower, max, min, mkdir, mkdtemp, next, object, open, parse_file, parse_ruby_file, patch, pop, range, read, read_text, register, release, replace, rfind, run, save_cached_nodes, save_config, save_manifest, set, signature, split, splitlines, stale_files, start, startswith, str, strip, time, unregister, update, update_meta, values, write, write_bytes, write_page, write_text
- **Called by:** indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/git.py::_run, indexer/git.py::changed_files_since, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::list_repos, indexer/rest_api.py::repo_detail, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::asyncio_coro, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** asyncio, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config._apply_env, indexer.config.load_config, indexer.config.save_config, indexer.embedding._call_embedding_api, indexer.embedding._get_openai_client, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_query, indexer.git.changed_files_since, indexer.grouper.density_group, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_embeddings, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_embeddings, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_wiki_pages, indexer.llm._FATAL_EXCEPTIONS, indexer.llm._anthropic_completion, indexer.llm._get_anthropic_client, indexer.llm._litellm_completion, indexer.llm.deep_enrich_index, indexer.llm.describe_files, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.rest_api.RepoRegistry, indexer.rest_api.TaskStore, indexer.rest_api._InvalidBodyError, indexer.rest_api._detect_default_branch, indexer.rest_api._discover_remote_branches, indexer.rest_api._get_repo_lock, indexer.rest_api._index_page, indexer.rest_api._locks_lock, indexer.rest_api._parse_body, indexer.rest_api._repo_locks, indexer.rest_api._run_indexing_pipeline, indexer.rest_api._run_rebuild_task_inner, indexer.rest_api._run_register_task_inner, indexer.rest_api._run_sync_task, indexer.rest_api._store_credentials, indexer.rest_api.get_source_context, indexer.rest_api.list_repos, indexer.rest_api.register_repo, indexer.rest_api.search_symbols, indexer.rest_api.tasks, indexer.rest_api.trace_call, indexer.rest_api.webhook_by_name, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.search_symbols, indexer.ruby_parser.parse_ruby_file, indexer.utils, indexer.utils._env_loaded, indexer.utils.load_env_file, indexer.vector_store, indexer.vector_store._build_meta, indexer.vector_store._get_client, indexer.vector_store._get_or_create_collection, indexer.vector_store._truncate_list, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, inspect, json, os, pathlib.Path, subprocess, tempfile, threading, time, unittest.mock.MagicMock, unittest.mock.patch
## Entry Points
- `test_parse_returns_nodes`
- `test_function_node`
- `test_method_node`
- `test_class_node`
- `test_docstring_extracted`
- `test_imports_extracted`
- `test_calls_extracted`
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
