# tests/

## Overview

This test suite validates a multi-language code analysis pipeline that parses source files (Python, Rust, Java, Ruby) into typed AST nodes (function, class, method, struct, trait, enum, interface, module, type alias, trait method spec) with associated metadata (docstrings, imports, calls). The core `parse_file` function extracts nodes and supports caching via `save_cached_nodes`/`load_cached_nodes` to avoid reparsing. Downstream modules (`Manifest`, `Grouper`, `Wiki`) consume these nodes for symbol organization, documentation generation, and optional fixes (`p1_fixes`). `Config` drives language-specific behavior and caching paths. The tests ensure cross-language node type detection, metadata extraction correctness, and cache roundtrip integrity.

## Modules
| File | Purpose |
|------|---------|
| tests/test_ast_parser.py | Tests for AST parser across languages |
| tests/test_manifest.py | Tests for manifest hash, save, load, and stale detection |
| tests/test_wiki.py | Tests for wiki page building, index, and symbol references |
| tests/test_p1_fixes.py | Regression tests for critical P1 bug fixes across multiple modules |
| tests/test_grouper.py | Tests for file grouping logic based on density |
| tests/test_config.py | Tests for configuration loading and saving |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function | Asserts parse_file returns at least one node |
| `tests/test_ast_parser.py::test_function_node` | function | Asserts parse_file returns node with type function |
| `tests/test_ast_parser.py::test_method_node` | function | Asserts parse_file returns node with type method |
| `tests/test_ast_parser.py::test_class_node` | function | Asserts parse_file returns node with type class |
| `tests/test_ast_parser.py::test_docstring_extracted` | function | Asserts docstring is non-empty for a parsed node |
| `tests/test_ast_parser.py::test_imports_extracted` | function | Asserts imports list is non-empty with strings |
| `tests/test_ast_parser.py::test_calls_extracted` | function | Asserts calls list is non-empty for a parsed node |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function | Tests saving and loading cached nodes preserves length |
| `tests/test_ast_parser.py::test_rust_parse_returns_nodes` | function | Asserts Rust parse returns at least one node |
| `tests/test_ast_parser.py::test_rust_function_node` | function | Asserts Rust parse returns a function node |
| `tests/test_ast_parser.py::test_rust_struct_node` | function | Asserts Rust parse returns a struct node |
| `tests/test_ast_parser.py::test_rust_method_node` | function | Asserts Rust parse returns a method node |
| `tests/test_ast_parser.py::test_rust_trait_node` | function | Asserts Rust parse returns a trait node |
| `tests/test_ast_parser.py::test_rust_trait_method_spec` | function | Asserts Rust parse returns a trait method spec node |
| `tests/test_ast_parser.py::test_rust_enum_node` | function | Asserts Rust parse returns an enum node |
| `tests/test_ast_parser.py::test_rust_type_alias` | function | Asserts Rust parse returns a type alias node |
| `tests/test_ast_parser.py::test_rust_docstring_extracted` | function | Asserts Rust docstring is non-empty for a node |
| `tests/test_ast_parser.py::test_rust_imports_extracted` | function | Asserts Rust imports list is non-empty with strings |
| `tests/test_ast_parser.py::test_java_parse_returns_nodes` | function | Asserts Java parse returns at least one node |
| `tests/test_ast_parser.py::test_java_class_node` | function | Asserts Java parse returns a class node |
| `tests/test_ast_parser.py::test_java_method_node` | function | Asserts Java parse returns a method node |
| `tests/test_ast_parser.py::test_java_interface_node` | function | Asserts Java parse returns an interface node |
| `tests/test_ast_parser.py::test_java_enum_node` | function | Asserts Java parse returns an enum node |
| `tests/test_ast_parser.py::test_java_javadoc_extracted` | function | Asserts Java docstring is non-empty and ends with dot |
| `tests/test_ast_parser.py::test_java_imports_extracted` | function | Asserts Java imports list is non-empty with strings |
| `tests/test_ast_parser.py::test_ruby_parse_returns_nodes` | function | Asserts Ruby parse returns at least one node |
| `tests/test_ast_parser.py::test_ruby_class_node` | function | Asserts Ruby parse returns a class node |
| `tests/test_ast_parser.py::test_ruby_method_node` | function | Asserts Ruby parse returns a method node |
| `tests/test_ast_parser.py::test_ruby_module_node` | function | Asserts Ruby parse returns a module node |
| `tests/test_ast_parser.py::test_ruby_function_node` | function | Asserts Ruby parse returns a function node |
| `tests/test_ast_parser.py::test_ruby_docstring_extracted` | function | Asserts Ruby docstring is non-empty and lowercase |
| `tests/test_config.py::_clean_env` | function | Removes test-related environment variables |
| `tests/test_config.py::_restore_env` | function | Restores original environment from saved state |
| `tests/test_config.py::test_load_defaults` | function | Asserts load_config returns Config with default values |
| `tests/test_config.py::test_save_and_reload` | function | Asserts saved then loaded Config matches original |
| `tests/test_config.py::test_partial_toml_uses_defaults` | function | Asserts partial TOML file merges with defaults |
| `tests/test_grouper.py::test_sparse_folders_merge_to_parent` | function | Asserts sparse subfolders merge into parent group |
| `tests/test_grouper.py::test_dense_folder_gets_own_page` | function | Asserts dense folder gets its own page group |
| `tests/test_grouper.py::test_different_folders_get_separate_groups` | function | Asserts different folders form separate groups |
| `tests/test_grouper.py::test_deep_sparse_merges_upward` | function | Asserts deep sparse structure merges upward |
| `tests/test_grouper.py::test_root_level_files` | function | Asserts root-level files are grouped together |
| `tests/test_grouper.py::test_returns_all_files` | function | Asserts density_group returns all input files |
| `tests/test_grouper.py::test_root_files_count_correctly` | function | Asserts root file count in each group is correct |
| `tests/test_manifest.py::test_compute_hash_stable` | function | Asserts compute_hash returns consistent hash for same content |
| `tests/test_manifest.py::test_empty_manifest_on_missing` | function | Asserts load_manifest returns empty dict for missing file |
| `tests/test_manifest.py::test_save_and_reload` | function | Asserts saved manifest reloads with same entries |
| `tests/test_manifest.py::test_stale_files_detected` | function |  |
| `tests/test_manifest.py::test_fresh_file_not_stale` | function |  |
| `tests/test_manifest.py::test_load_manifest_missing_component_ids` | function |  |
| `tests/test_wiki.py::_make_node` | function | Creates an ASTNode for test wiki page building |
| `tests/test_wiki.py::test_build_page_contains_symbol` | function | Verifies build_page includes symbol in output |
| `tests/test_wiki.py::test_build_page_contains_calls` | function | Checks build_page includes calls in output |
| `tests/test_wiki.py::test_build_page_contains_called_by` | function | Checks build_page includes called_by in output |
| `tests/test_wiki.py::test_build_page_no_agent_hints` | function | Verifies build_page excludes agent hints |
| `tests/test_wiki.py::test_build_index_contains_page` | function | Checks build_index includes page entry |
| `tests/test_wiki.py::test_write_page_creates_file` | function | Verifies write_page creates file on disk |
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
| `tests/test_p1_fixes.py::TestLoadReposHasCatch.test_loadrepos_has_catch` | method | Checks load_repos source contains try-except for error handling |
| `tests/test_p1_fixes.py::TestAnthropicImport` | class | Tests that anthropic module is imported in completion |
| `tests/test_p1_fixes.py::TestAnthropicImport.test_anthropic_imported_in_completion` | method | Verifies anthropic import present in completion module |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions` | class | Tests retry uses FATAL_EXCEPTIONS constant |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions.test_retry_uses_fatal_exceptions_constant` | method | Verifies retry logic references FATAL_EXCEPTIONS constant |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone` | class | Tests delete_by_files passes dim=None |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone.test_delete_by_files_passes_dim_none` | method | Checks delete_by_files passes dim=None argument |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid` | class | Tests all_new_ids uses valid_only flag |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid.test_all_new_ids_uses_valid_only` | method | Verifies all_new_ids includes valid_only parameter |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch` | class | Tests open_repo function has try-except block |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch.test_openrepo_has_catch` | method | Checks open_repo source contains try-except |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch` | class | Tests do_search function has try-except block |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch.test_dosearch_has_catch` | method | Checks do_search source contains try-except |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped` | class | Tests trace_call max depth is clamped |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped.test_trace_call_max_depth_clamped` | method | Verifies trace_call max_depth is clamped to upper bound |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound` | class | Tests trace_call max depth has lower bound |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound.test_trace_call_max_depth_lower_bound` | method | Checks trace_call max_depth has minimum value |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation` | class | Tests type validation for tags and branches |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation.test_tags_type_validation` | method | Verifies tags parameter type is validated |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy` | class | Tests build_batches includes called_by field |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy.test_build_batches_includes_called_by` | method | Checks build_batches output contains called_by |
| `tests/test_p1_fixes.py::TestRound14Fixes` | class | Tests multiple round 14 bug fixes |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_ls_remote` | method | Verifies git terminal prompt disabled for ls-remote |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_store_credentials` | method | Checks git terminal prompt disabled when storing credentials |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_expand_depth_lower_bound` | method | Verifies expand_depth has a lower bound |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_url_empty_check_before_discovery` | method | Checks URL is checked for emptiness before discovery |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_no_duplicate_url_validation` | method | Ensures no duplicate URL validation logic |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_git_add_timeout` | method | Verifies CLI git add command has a timeout |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_warnings_warn` | method | Checks CLI does not use warnings.warn |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_unused_imports` | method | Verifies CLI module has no unused imports |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_unused_config_imports` | method | Checks REST API module has no unused config imports |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_mcp_no_unused_socket_import` | method | Verifies MCP module has no unused socket import |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_max_depth_limit_consistent` | method | Ensures max_depth limit is consistent |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_retrieval_branch_empty_means_no_filter` | method | Verifies empty retrieval branch results in no filter |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_uses_retrieval_trace_call` | method | Checks REST API endpoints use retrieval trace_call |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_duplicate_parse_json_list` | method | Ensures REST API has no duplicate parse_json_list |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_description_type_validation` | method | Verifies description parameter type is validated |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_tags_element_type_validation` | method | Checks tags list elements are type validated |
| `tests/test_p1_fixes.py::TestRound15Fixes` | class | Tests multiple round 15 bug fixes |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_manifest` | method | Verifies open_repo safely handles null manifest |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_wiki_pages` | method | Checks open_repo safely handles null wiki pages |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_api_json_parse_error_handling` | method | Verifies API catches and handles JSON parse errors |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_sync_branch_has_try_catch` | method | Checks sync_branch function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_rebuild_branch_has_try_catch` | method | Verifies rebuild_branch function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_register_missing_branch_has_try_catch` | method | Ensures register_missing_branch uses try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_unregister_has_try_catch` | method | Checks do_unregister function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_validate_has_try_catch` | method | Verifies do_validate function uses try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_querySelector_title_optional_chaining` | method | Checks querySelector uses optional chaining for title |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_assert_operator_precedence_fixed` | method | Verifies assertion operator precedence is correct |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_no_duplicate_anthropic_lock_test` | method | Ensures no duplicate test for anthropic lock |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_indexer_toml_no_dashscope_hardcoded` | method | Verifies indexer.toml has no hardcoded dashscope reference |
| `tests/test_p1_fixes.py::TestRound16Fixes` | class | Tests multiple round 16 bug fixes |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_rebuild_git_before_delete` | method | Verifies git rebuild occurs before directory deletion |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_branch_detection_after_clone` | method | Checks branch detection happens after clone |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_upsert_before_manifest` | method | Ensures vector upsert occurs before manifest update |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_progress_offset_in_pipeline` | method | Verifies progress offset is used in pipeline |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_sync_repo_url_initialized_before_try` | method | Checks sync_repo URL variable initialized before try block |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_clone_dir_cleanup_on_failure` | method | Verifies clone directory cleanup occurs on failure |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_eviction` | method | Tests vector store client eviction function exists |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_lock` | method | Verifies vector store client uses a lock |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_empty_branches_to_index_check` | method | Checks empty branches_to_index is handled |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_timeout_expired_includes_cmd` | method | Verifies timeout_expired message includes command |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_skill_metadata_not_zero` | method | Ensures skill metadata is non-zero value |
| `tests/test_p1_fixes.py::TestRound17Fixes` | class | Tests multiple round 17 bug fixes |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_register_task_no_undefined_description_tags` | method | Verifies register_task handles undefined description or tags |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_unregister_uses_root_not_path` | method | Checks unregister uses root attribute, not path |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_search_symbols_int_coercion` | method | Verifies search_symbols coerces parameters to int |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_trace_call_int_coercion` | method | Checks trace_call coerces max_depth to int |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_git_config_has_timeout` | method | Verifies git config enforces a timeout |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_detect_default_branch_has_git_terminal_prompt` | method | Checks detect_default_branch disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_rebuild_evicts_vector_client_before_rmtree` | method | Ensures rebuild evicts vector client before removing directory |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_api_parses_json_error_body` | method | Verifies API parses JSON error body on failure |
| `tests/test_p1_fixes.py::TestRound18Fixes` | class | Tests multiple round 18 bug fixes |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_rebuild_has_timeout_expired_handler` | method | Verifies rebuild handles TimeoutExpired exception |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_py_has_git_terminal_prompt` | method | Checks git.py disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_cli_git_add_has_git_terminal_prompt` | method | Verifies CLI git add disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_step_names_includes_git_steps` | method | Ensures step names include git-related steps |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_evict_client_logs_on_failure` | method | Verifies evict_client logs errors on failure |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_reset_return_code_checked` | method | Checks git reset return code is validated |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations` | class | Tests performance optimization features |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_description_cache_functions_exist` | method | Verifies description cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_file_description_cache_functions_exist` | method | Checks file description cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_description_cache` | method | Ensures pipeline uses description cache for efficiency |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_file_description_cache` | method | Verifies pipeline uses file description cache |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_batch_size_increased` | method | Checks embedding batch size is increased |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_describe_files_parallel` | method | Verifies describe_files runs in parallel |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parse_candidates_parallel` | method | Ensures parse_candidates runs in parallel |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_vector_store_batch_query` | method | Checks vector store uses batch query |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_cache_functions_exist` | method | Verifies embedding cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_upsert_vectors_uses_embedding_cache` | method | Ensures upsert_vectors uses embedding cache |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parallel_symbol_and_file_description` | method | Tests parallel processing for symbol and file description |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_write_wiki_pages_accepts_precomputed_groups` | method | Verifies write_wiki_pages accepts precomputed groups |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_load_existing_nodes_uses_manifest_hash` | method | Checks load_existing_nodes uses manifest hash for caching |
| `tests/test_p1_fixes.py::_coro` | function | Defines a coroutine helper for async tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::register_repo` | function | Registers a repository for testing with mocked path |
| `tests/test_p1_fixes.py::unregister_repo` | function | Unregisters a repository for testing |
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
| `tests/test_p1_fixes.py::TestLoadReposHasCatch.test_loadrepos_has_catch` | method | Checks load_repos source contains try-except for error handling |
| `tests/test_p1_fixes.py::TestAnthropicImport` | class | Tests that anthropic module is imported in completion |
| `tests/test_p1_fixes.py::TestAnthropicImport.test_anthropic_imported_in_completion` | method | Verifies anthropic import present in completion module |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions` | class | Tests retry uses FATAL_EXCEPTIONS constant |
| `tests/test_p1_fixes.py::TestRetryFatalExceptions.test_retry_uses_fatal_exceptions_constant` | method | Verifies retry logic references FATAL_EXCEPTIONS constant |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone` | class | Tests delete_by_files passes dim=None |
| `tests/test_p1_fixes.py::TestDeleteByFilesDimNone.test_delete_by_files_passes_dim_none` | method | Checks delete_by_files passes dim=None argument |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid` | class | Tests all_new_ids uses valid_only flag |
| `tests/test_p1_fixes.py::TestAllNewIdsOnlyValid.test_all_new_ids_uses_valid_only` | method | Verifies all_new_ids includes valid_only parameter |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch` | class | Tests open_repo function has try-except block |
| `tests/test_p1_fixes.py::TestOpenRepoHasCatch.test_openrepo_has_catch` | method | Checks open_repo source contains try-except |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch` | class | Tests do_search function has try-except block |
| `tests/test_p1_fixes.py::TestDoSearchHasCatch.test_dosearch_has_catch` | method | Checks do_search source contains try-except |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped` | class | Tests trace_call max depth is clamped |
| `tests/test_p1_fixes.py::TestMCPMaxDepthClamped.test_trace_call_max_depth_clamped` | method | Verifies trace_call max_depth is clamped to upper bound |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound` | class | Tests trace_call max depth has lower bound |
| `tests/test_p1_fixes.py::TestTraceCallMaxDepthLowerBound.test_trace_call_max_depth_lower_bound` | method | Checks trace_call max_depth has minimum value |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation` | class | Tests type validation for tags and branches |
| `tests/test_p1_fixes.py::TestTagsBranchesTypeValidation.test_tags_type_validation` | method | Verifies tags parameter type is validated |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy` | class | Tests build_batches includes called_by field |
| `tests/test_p1_fixes.py::TestBuildBatchesIncludesCalledBy.test_build_batches_includes_called_by` | method | Checks build_batches output contains called_by |
| `tests/test_p1_fixes.py::TestRound14Fixes` | class | Tests multiple round 14 bug fixes |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_ls_remote` | method | Verifies git terminal prompt disabled for ls-remote |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_git_terminal_prompt_on_store_credentials` | method | Checks git terminal prompt disabled when storing credentials |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_expand_depth_lower_bound` | method | Verifies expand_depth has a lower bound |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_url_empty_check_before_discovery` | method | Checks URL is checked for emptiness before discovery |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_no_duplicate_url_validation` | method | Ensures no duplicate URL validation logic |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_git_add_timeout` | method | Verifies CLI git add command has a timeout |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_warnings_warn` | method | Checks CLI does not use warnings.warn |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_cli_no_unused_imports` | method | Verifies CLI module has no unused imports |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_unused_config_imports` | method | Checks REST API module has no unused config imports |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_mcp_no_unused_socket_import` | method | Verifies MCP module has no unused socket import |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_max_depth_limit_consistent` | method | Ensures max_depth limit is consistent |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_retrieval_branch_empty_means_no_filter` | method | Verifies empty retrieval branch results in no filter |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_uses_retrieval_trace_call` | method | Checks REST API endpoints use retrieval trace_call |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_rest_api_no_duplicate_parse_json_list` | method | Ensures REST API has no duplicate parse_json_list |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_description_type_validation` | method | Verifies description parameter type is validated |
| `tests/test_p1_fixes.py::TestRound14Fixes.test_tags_element_type_validation` | method | Checks tags list elements are type validated |
| `tests/test_p1_fixes.py::TestRound15Fixes` | class | Tests multiple round 15 bug fixes |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_manifest` | method | Verifies open_repo safely handles null manifest |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_open_repo_null_safe_wiki_pages` | method | Checks open_repo safely handles null wiki pages |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_api_json_parse_error_handling` | method | Verifies API catches and handles JSON parse errors |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_sync_branch_has_try_catch` | method | Checks sync_branch function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_rebuild_branch_has_try_catch` | method | Verifies rebuild_branch function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_register_missing_branch_has_try_catch` | method | Ensures register_missing_branch uses try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_unregister_has_try_catch` | method | Checks do_unregister function encloses in try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_do_validate_has_try_catch` | method | Verifies do_validate function uses try-except |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_querySelector_title_optional_chaining` | method | Checks querySelector uses optional chaining for title |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_assert_operator_precedence_fixed` | method | Verifies assertion operator precedence is correct |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_no_duplicate_anthropic_lock_test` | method | Ensures no duplicate test for anthropic lock |
| `tests/test_p1_fixes.py::TestRound15Fixes.test_indexer_toml_no_dashscope_hardcoded` | method | Verifies indexer.toml has no hardcoded dashscope reference |
| `tests/test_p1_fixes.py::TestRound16Fixes` | class | Tests multiple round 16 bug fixes |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_rebuild_git_before_delete` | method | Verifies git rebuild occurs before directory deletion |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_branch_detection_after_clone` | method | Checks branch detection happens after clone |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_upsert_before_manifest` | method | Ensures vector upsert occurs before manifest update |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_progress_offset_in_pipeline` | method | Verifies progress offset is used in pipeline |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_sync_repo_url_initialized_before_try` | method | Checks sync_repo URL variable initialized before try block |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_clone_dir_cleanup_on_failure` | method | Verifies clone directory cleanup occurs on failure |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_eviction` | method | Tests vector store client eviction function exists |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_vector_store_client_lock` | method | Verifies vector store client uses a lock |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_empty_branches_to_index_check` | method | Checks empty branches_to_index is handled |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_timeout_expired_includes_cmd` | method | Verifies timeout_expired message includes command |
| `tests/test_p1_fixes.py::TestRound16Fixes.test_skill_metadata_not_zero` | method | Ensures skill metadata is non-zero value |
| `tests/test_p1_fixes.py::TestRound17Fixes` | class | Tests multiple round 17 bug fixes |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_register_task_no_undefined_description_tags` | method | Verifies register_task handles undefined description or tags |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_unregister_uses_root_not_path` | method | Checks unregister uses root attribute, not path |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_search_symbols_int_coercion` | method | Verifies search_symbols coerces parameters to int |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_trace_call_int_coercion` | method | Checks trace_call coerces max_depth to int |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_git_config_has_timeout` | method | Verifies git config enforces a timeout |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_detect_default_branch_has_git_terminal_prompt` | method | Checks detect_default_branch disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_rebuild_evicts_vector_client_before_rmtree` | method | Ensures rebuild evicts vector client before removing directory |
| `tests/test_p1_fixes.py::TestRound17Fixes.test_api_parses_json_error_body` | method | Verifies API parses JSON error body on failure |
| `tests/test_p1_fixes.py::TestRound18Fixes` | class | Tests multiple round 18 bug fixes |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_rebuild_has_timeout_expired_handler` | method | Verifies rebuild handles TimeoutExpired exception |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_py_has_git_terminal_prompt` | method | Checks git.py disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_cli_git_add_has_git_terminal_prompt` | method | Verifies CLI git add disables git terminal prompt |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_step_names_includes_git_steps` | method | Ensures step names include git-related steps |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_evict_client_logs_on_failure` | method | Verifies evict_client logs errors on failure |
| `tests/test_p1_fixes.py::TestRound18Fixes.test_git_reset_return_code_checked` | method | Checks git reset return code is validated |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations` | class | Tests performance optimization features |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_description_cache_functions_exist` | method | Verifies description cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_file_description_cache_functions_exist` | method | Checks file description cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_description_cache` | method | Ensures pipeline uses description cache for efficiency |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_pipeline_uses_file_description_cache` | method | Verifies pipeline uses file description cache |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_batch_size_increased` | method | Checks embedding batch size is increased |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_describe_files_parallel` | method | Verifies describe_files runs in parallel |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parse_candidates_parallel` | method | Ensures parse_candidates runs in parallel |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_vector_store_batch_query` | method | Checks vector store uses batch query |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_embedding_cache_functions_exist` | method | Verifies embedding cache functions are defined |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_upsert_vectors_uses_embedding_cache` | method | Ensures upsert_vectors uses embedding cache |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_parallel_symbol_and_file_description` | method | Tests parallel processing for symbol and file description |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_write_wiki_pages_accepts_precomputed_groups` | method | Verifies write_wiki_pages accepts precomputed groups |
| `tests/test_p1_fixes.py::TestPerformanceOptimizations.test_load_existing_nodes_uses_manifest_hash` | method | Checks load_existing_nodes uses manifest hash for caching |
| `tests/test_p1_fixes.py::_coro` | function | Defines a coroutine helper for async tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::run` | function | Invokes parsing and source context setup for tests |
| `tests/test_p1_fixes.py::register_repo` | function | Registers a repository for testing with mocked path |
| `tests/test_p1_fixes.py::unregister_repo` | function | Unregisters a repository for testing |
## Data Flows
- Source file → parse_file → node extraction (type, docstring, imports, calls) → save_cached_nodes to disk
- load_cached_nodes → grouper aggregates symbols by file/module → manifest updated with file metadata
- Manifest → wiki generator renders documentation pages from organized symbol tree
## Design Constraints
- Each source file must produce at least one node; parse_file does not handle empty files gracefully (returns empty list).
- Docstrings in Java must end with a period (asserted by test_java_javadoc_extracted); other languages have no such requirement.
- Cache roundtrip is tested only for Python nodes; other languages rely on general parse test coverage.
- Imports list is guaranteed to contain only strings (enforced via isinstance check per language).
- Rust enum and type alias node type names end with '_enum' and '_type_alias' respectively; trait method spec is a distinct node type.
- Ruby function and module nodes are type-checked via name ending with '_function' or '_module' (not present in Python/Java).
## Relationships
- **Calls:** ASTNode, Config, EmbeddingConfig, Exception, FileEntry, IndexEntry, MagicMock, Manifest, NamedTemporaryFile, PageContext, Path, RLock, RepoRegistry, TaskStore, TemporaryDirectory, Thread, __import__, _apply_env, _clean_env, _cleanup, _coro, _expand_with_call_graph, _get_repo_lock, _make_node, _parse_body, _restore_env, _run_rebuild_task_inner, _truncate_list, acquire, all, any, append, asyncio_coro, build_batches, build_index, build_page, callable, changed_files_since, compare_digest, compute_hash, count, create, cross_reference, density_group, dict, dumps, embed_query, endswith, exists, find, get, get_source_context, getsource, hasattr, index, isinstance, items, join, keys, len, list, load_cached_nodes, load_config, load_env_file, load_manifest, loads, lower, max, min, mkdir, mkdtemp, next, object, open, parse_file, parse_ruby_file, patch, pop, range, read, read_text, readlines, register, release, replace, rfind, run, save_cached_nodes, save_config, save_manifest, set, signature, split, splitlines, stale_files, start, startswith, str, strip, time, unregister, update, update_meta, values, write, write_bytes, write_page, write_text
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
