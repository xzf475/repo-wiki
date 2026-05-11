# tests/

## Overview

This test suite validates the core modules of the codebase: AST parsing (Python, Rust, Java, Ruby via `ast_parser`), configuration loading (`config`), code grouping (`grouper`), wiki generation (`wiki`), manifest building (`manifest`), and p1 fixes (`p1_fixes`). It ensures correctness of node extraction, caching, and output formatting across multiple languages and edge cases (empty files, unsupported extensions, complex code structures). The tests are critical for catching regressions when the AST parser or downstream modules are modified. Key fixtures include inline code snippets and temporary directories for cache round-trips.

## Modules
| File | Purpose |
|------|---------|
| tests/test_config.py |  |
| tests/test_grouper.py |  |
| tests/test_wiki.py |  |
| tests/test_manifest.py |  |
| tests/test_ast_parser.py |  |
| tests/test_p1_fixes.py | Test suite for various module fixes and validations |
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
| `tests/test_p1_fixes.py::TestTaskStore` | class | Test suite for TaskStore create, update, get, cleanup |
| `tests/test_p1_fixes.py::TestTaskStore.test_create_task` | method | Tests that create stores a task and get retrieves it |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_task` | method | Tests that update modifies an existing task fields |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp` | method | Tests that update with finished status sets timestamp |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop` | method | Tests that updating nonexistent task does nothing |
| `tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none` | method | Tests that get returns None for nonexistent task ID |
| `tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks` | method | Tests that cleanup removes expired tasks from store |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety` | class | Tests thread safety of RepoRegistry register/unregister |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register` | method | Tests concurrent register calls succeed without races |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister` | method | Tests concurrent unregister calls succeed without races |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock` | class | Test suite for skip-lock mechanism in repo locking |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release` | method | Tests that skip-lock does not release acquired lock |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent` | method | Tests that normal lock blocks concurrent access |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone` | class | Tests get returns None for nonexistent repos |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none` | method | Tests get on nonexistent path returns None |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely` | method | Tests get safely returns None without side effects |
| `tests/test_p1_fixes.py::TestParseBody` | class | Tests _parse_body function parsing JSON request body |
| `tests/test_p1_fixes.py::TestParseBody.test_valid_json` | method | Tests valid JSON returns parsed dict |
| `tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty` | method | Tests invalid JSON returns empty dict |
| `tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty` | method | Tests non-dict JSON returns empty dict |
| `tests/test_p1_fixes.py::asyncio_coro` | function | Returns async coroutine function for mocking |
| `tests/test_p1_fixes.py::TestManifestFieldValidation` | class | Tests manifest field defaults when missing |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty` | method | Tests missing component_ids defaults to empty list |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty` | method | Tests missing hash field defaults to empty string |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty` | method | Tests corrupt JSON manifest returns empty default dict |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString` | class | Tests empty env string does not override default config |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default` | method | Tests empty env string leaves default config value unchanged |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck` | class | Tests git checkout failure sets task status to failed |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed` | method | Tests git non-zero return sets task to failed |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers` | class | Tests cross-reference merging caller lists across files |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers` | method | Tests cross-reference combines same-file and cross-file callers |
| `tests/test_p1_fixes.py::TestUpdateMetaLock` | class | Tests update_meta uses a lock |
| `tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock` | method | Tests update_meta acquires and releases a lock |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping` | class | Tests stripping quotes from env file values |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped` | method | Tests double quotes stripped from env values |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped` | method | Tests single quotes stripped from env values |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList` | class | Tests _truncate_list produces valid JSON |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json` | method | Tests truncated list output is valid JSON |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated` | method | Tests small lists remain unchanged |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion` | class | Tests string params converted to int in get_source_context |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int` | method | Tests string line numbers coerced to int |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock` | class | Tests unregister removes the repo lock file |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock` | method | Tests unregister deletes the lock file |
| `tests/test_p1_fixes.py::TestAtomicWrites` | class | Tests atomic writes of config and manifest files |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic` | method | Tests save_config writes atomically without temp file persisting |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic` | method | Tests save_manifest writes atomically |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause` | class | Tests single branch retrieval using where clause |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause` | method | Tests get for single branch uses a where clause |
| `tests/test_p1_fixes.py::TestIntParamValidation` | class | Tests integer param validation returns 400 on invalid |
| `tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400` | method | Tests invalid line_start returns 400 status |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy` | class | Tests webhook branch list is not mutated |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy.test_webhook_branch_list_not_mutated` | method | Tests webhook processing does not modify original branch list |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning` | class | Tests cleanup does not evict running tasks |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks` | method | Tests cleanup skips tasks with running status |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse` | class | Tests embed_query raises on empty response |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty` | method | Tests empty embedding response raises exception |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone` | class | Tests compute_hash returns None on OS error |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror` | method | Tests compute_hash returns None on file read error |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit` | class | Tests changed_files_since raises on invalid commit |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit` | method | Tests invalid commit hash raises exception |
| `tests/test_p1_fixes.py::TestExpansionCap` | class | Tests _expand_with_call_graph respects max expansion limit |
| `tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max` | method | Tests expansion stops at max depth |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion` | class | Tests expansion caps at max with actual expansions |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max` | method | Tests expansion caps at max even with many candidates |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape` | class | Tests script tag escaping in API key dumps |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape.test_api_key_script_tag_escaped` | method | Tests script tags in API key are escaped in JSON dump |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive` | class | Tests case-insensitive Bearer token parsing |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive.test_lowercase_bearer_accepted` | method | Tests lowercase bearer prefix is accepted |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK` | class | Tests CJK token estimation uses triple character budget |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple` | method | Tests CJK characters count triple towards token budget |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock` | class | Tests reentrant lock prevents deadlock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock` | method | Tests register does not deadlock when using reentrant lock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_rlock_allows_reentrant` | method | Tests reentrant lock allows nested acquires |
| `tests/test_p1_fixes.py::TestTopKNegativeValue` | class | Tests clamping negative top_k values to one |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_negative_clamped_to_one` | method | Tests negative top_k clamped to 1 |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_zero_clamped_to_one` | method | Tests zero top_k clamped to 1 |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_normal_value` | method | Tests positive top_k remains unchanged |
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
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset` | method | Tests invalid max_tokens_per_batch resets to default |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset` | method | Tests invalid dimensions resets to default |
| `tests/test_p1_fixes.py::TestRubyModuleMethod` | class | Tests Ruby module method naming with prefix |
| `tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix` | method | Tests module methods include the module prefix |
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
| `tests/test_p1_fixes.py::register_repo` | function | Registers a test repository by creating directories and writing configuration files |
| `tests/test_p1_fixes.py::unregister_repo` | function | Unregisters a test repository by appending to list and calling unregister |
## Data Flows
- test harness calls `parse_file(sample_code, '.py')` → returns list of `Node` objects → each node's type, name, docstring, imports, and calls are asserted.
- cache round-trip: `parse_file` → `save_cached_nodes` writes JSON → `load_cached_nodes` reads and returns list → original and reloaded nodes are compared by length.
- language-specific tests (Rust, Java, Ruby) each call `parse_file` with appropriate sample code and extension → assert presence of expected node types (struct, class, method, trait, enum, module) using `any()` and `endswith()` for names.
## Design Constraints
- `parse_file` selects parser based on file extension; unsupported extensions raise an exception, tested implicitly by skipping other languages.
- Cache serialization uses JSON; node objects must be serializable (e.g., `Node` is a dataclass with simple fields), and `load_cached_nodes` reconstructs them without accessing the original code.
- The docstring extraction test (`test_docstring_extracted`) assumes the first node in the returned list carries the docstring; it fails if node ordering changes.
- Import extraction tests (`test_imports_extracted`) use `isinstance` with a tuple of node types, requiring the exact types (e.g., `ImportNode`, `ImportFromNode`) to match.
- All inline sample code is embedded as raw strings in test functions; modifications to parser behavior may require updating samples that rely on specific node order or attribute values.
- The cache round-trip test uses `TemporaryDirectory` to ensure cleanup; it assumes the cache directory is writable and non‑existent initially.
## Relationships
- **Calls:** ASTNode, Config, EmbeddingConfig, Exception, FileEntry, IndexEntry, MagicMock, Manifest, NamedTemporaryFile, PageContext, Path, RLock, RepoRegistry, TaskStore, TemporaryDirectory, Thread, __import__, _apply_env, _clean_env, _cleanup, _coro, _expand_with_call_graph, _get_repo_lock, _make_node, _parse_body, _restore_env, _run_rebuild_task_inner, _truncate_list, acquire, all, any, append, asyncio_coro, build_batches, build_index, build_page, callable, changed_files_since, compare_digest, compute_hash, count, create, cross_reference, density_group, dict, dumps, embed_query, endswith, exists, find, get, get_source_context, getsource, hasattr, index, isinstance, items, join, keys, len, list, load_cached_nodes, load_config, load_env_file, load_manifest, loads, lower, max, min, mkdir, mkdtemp, next, object, open, parse_file, parse_ruby_file, patch, pop, range, read, read_text, register, release, replace, rfind, run, save_cached_nodes, save_config, save_manifest, set, signature, split, splitlines, stale_files, start, startswith, str, strip, time, unregister, update, update_meta, values, write, write_bytes, write_page, write_text
- **Called by:** indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/git.py::_run, indexer/git.py::_run_checked, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::list_repos, indexer/rest_api.py::repo_detail, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::asyncio_coro, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** asyncio, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config._apply_env, indexer.config.load_config, indexer.config.save_config, indexer.embedding._call_embedding_api, indexer.embedding._get_openai_client, indexer.embedding.compute_embedding_sig, indexer.embedding.embed_query, indexer.git.changed_files_since, indexer.git_ops.GitOperationError, indexer.git_ops._detect_default_branch, indexer.grouper.density_group, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_cached_descriptions, indexer.indexing.load_cached_embeddings, indexer.indexing.load_cached_file_descriptions, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.prepare_descriptions, indexer.indexing.save_cached_descriptions, indexer.indexing.save_cached_embeddings, indexer.indexing.save_cached_file_descriptions, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_wiki_pages, indexer.llm._anthropic_completion, indexer.llm._get_anthropic_client, indexer.llm._litellm_completion, indexer.llm.deep_enrich_index, indexer.llm.describe_files, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.rest_api.RepoRegistry, indexer.rest_api.TaskStore, indexer.rest_api._InvalidBodyError, indexer.rest_api._discover_remote_branches, indexer.rest_api._get_repo_lock, indexer.rest_api._index_page, indexer.rest_api._locks_lock, indexer.rest_api._parse_body, indexer.rest_api._repo_locks, indexer.rest_api._run_indexing_pipeline, indexer.rest_api._run_rebuild_task_inner, indexer.rest_api._run_register_task_inner, indexer.rest_api._run_sync_task, indexer.rest_api._store_credentials, indexer.rest_api.get_source_context, indexer.rest_api.list_repos, indexer.rest_api.register_repo, indexer.rest_api.search_symbols, indexer.rest_api.tasks, indexer.rest_api.trace_call, indexer.rest_api.webhook_by_name, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.retrieval.search_symbols, indexer.ruby_parser.parse_ruby_file, indexer.utils, indexer.utils.FATAL_EXCEPTIONS, indexer.utils._env_loaded, indexer.utils.load_env_file, indexer.vector_store, indexer.vector_store._build_meta, indexer.vector_store._get_client, indexer.vector_store._get_or_create_collection, indexer.vector_store._truncate_list, indexer.vector_store.delete_by_files, indexer.vector_store.evict_client, indexer.vector_store.search, indexer.vector_store.upsert_nodes, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, inspect, json, os, pathlib.Path, subprocess, tempfile, threading, time, unittest.mock.MagicMock, unittest.mock.patch
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
