# tests/

## Modules
| File | Purpose |
|------|---------|
| tests/__init__.py |  |
| tests/test_agent_cli.py |  |
| tests/test_api_contracts.py |  |
| tests/test_ast_parser.py |  |
| tests/test_config.py |  |
| tests/test_grouper.py |  |
| tests/test_performance_baseline.py |  |
| tests/test_repository_adapters.py |  |
| tests/test_repository_index.py |  |
| tests/test_runtime_safety.py |  |
| tests/test_wiki.py |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_agent_cli.py::test_agent_capabilities_cli_outputs_contract` | function |  |
| `tests/test_agent_cli.py::test_agent_schema_cli_outputs_openapi_contract` | function |  |
| `tests/test_agent_cli.py::test_agent_context_cli_requires_symbol_id` | function |  |
| `tests/test_api_contracts.py::test_agent_capabilities_all_tools_have_schemas` | function |  |
| `tests/test_api_contracts.py::test_core_tool_contract_top_level_keys` | function |  |
| `tests/test_api_contracts.py::test_agent_capabilities_endpoint_contract` | function |  |
| `tests/test_api_contracts.py::test_agent_schema_endpoint_exports_machine_readable_contract` | function |  |
| `tests/test_api_contracts.py::test_stable_symbol_id_endpoint_contract` | function |  |
| `tests/test_api_contracts.py::test_post_edit_verify_endpoint_rejects_oversized_diff` | function |  |
| `tests/test_api_contracts.py::test_agent_modules_expose_split_boundaries` | function |  |
| `tests/test_api_contracts.py::test_agent_split_modules_own_function_bodies` | function |  |
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function |  |
| `tests/test_ast_parser.py::test_function_node` | function |  |
| `tests/test_ast_parser.py::test_method_node` | function |  |
| `tests/test_ast_parser.py::test_class_node` | function |  |
| `tests/test_ast_parser.py::test_docstring_extracted` | function |  |
| `tests/test_ast_parser.py::test_imports_extracted` | function |  |
| `tests/test_ast_parser.py::test_calls_extracted` | function |  |
| `tests/test_ast_parser.py::test_python_fastapi_route_entry_point` | function |  |
| `tests/test_ast_parser.py::test_python_click_command_entry_point` | function |  |
| `tests/test_ast_parser.py::test_typescript_import_type_array_in_generic_preserves_structure` | function |  |
| `tests/test_ast_parser.py::test_typescript_import_types_in_generic_calls_preserve_structure` | function |  |
| `tests/test_ast_parser.py::test_typescript_runtime_dynamic_import_is_not_normalized` | function |  |
| `tests/test_ast_parser.py::test_tsx_typeof_import_in_zero_arg_generic_call_is_valid` | function |  |
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
| `tests/test_performance_baseline.py::test_repository_index_generation_cost_scales_with_delta` | function |  |
| `tests/test_repository_adapters.py::_git` | function |  |
| `tests/test_repository_adapters.py::_commit` | function |  |
| `tests/test_repository_adapters.py::_repository` | function |  |
| `tests/test_repository_adapters.py::_registered_rest_repo` | function |  |
| `tests/test_repository_adapters.py::test_retrieval_and_service_return_the_same_generation_and_order` | function |  |
| `tests/test_repository_adapters.py::test_rest_search_requires_explicit_branch_and_preserves_scope` | function |  |
| `tests/test_repository_adapters.py::test_rest_local_repo_uses_current_branch_when_registry_has_no_branch` | function |  |
| `tests/test_repository_adapters.py::test_rest_trace_rejects_unknown_branch` | function |  |
| `tests/test_repository_adapters.py::test_update_repo_and_sync_discovers_branch_with_repo_credentials` | function |  |
| `tests/test_repository_adapters.py::discover` | function |  |
| `tests/test_repository_adapters.py::run_all` | function |  |
| `tests/test_repository_adapters.py::test_update_repo_and_sync_rejects_unmatched_rule_without_syncing_old_branches` | function |  |
| `tests/test_repository_adapters.py::test_agent_context_and_diagnostics_read_repository_generation` | function |  |
| `tests/test_repository_adapters.py::test_branch_status_isolated_in_same_database` | function |  |
| `tests/test_repository_adapters.py::test_remote_tracking_ref_wins_over_stale_local_branch` | function |  |
| `tests/test_repository_index.py::_git` | function |  |
| `tests/test_repository_index.py::_commit` | function |  |
| `tests/test_repository_index.py::_write_repository` | function |  |
| `tests/test_repository_index.py::_index` | function |  |
| `tests/test_repository_index.py::FakeEmbeddingProvider` | class |  |
| `tests/test_repository_index.py::FakeEmbeddingProvider.__init__` | method |  |
| `tests/test_repository_index.py::FakeEmbeddingProvider.embed_documents` | method |  |
| `tests/test_repository_index.py::FakeEmbeddingProvider.embed_query` | method |  |
| `tests/test_repository_index.py::FakeEmbeddingProvider._vector` | method |  |
| `tests/test_repository_index.py::test_sync_publishes_generation_and_inspect_reports_same_snapshot` | function |  |
| `tests/test_repository_index.py::test_symbols_project_current_generation_with_resolved_relations` | function |  |
| `tests/test_repository_index.py::test_trace_reads_current_generation_call_graph_in_both_directions` | function |  |
| `tests/test_repository_index.py::test_wiki_projection_is_rendered_from_published_generation` | function |  |
| `tests/test_repository_index.py::test_cli_run_and_status_use_repository_generation` | function |  |
| `tests/test_repository_index.py::test_unchanged_tree_is_constant_work_and_does_not_parse` | function |  |
| `tests/test_repository_index.py::unexpected_parse` | function |  |
| `tests/test_repository_index.py::test_incremental_sync_updates_and_removes_only_changed_paths` | function |  |
| `tests/test_repository_index.py::test_same_blob_is_parsed_once_across_branches` | function |  |
| `tests/test_repository_index.py::test_blob_artifact_survives_rename_without_stale_component_ids` | function |  |
| `tests/test_repository_index.py::test_non_source_tree_change_publishes_snapshot_without_parsing` | function |  |
| `tests/test_repository_index.py::test_staged_revision_captures_index_without_changing_git_state` | function |  |
| `tests/test_repository_index.py::test_worktree_revision_captures_unstaged_and_untracked_without_staging` | function |  |
| `tests/test_repository_index.py::test_parse_failure_does_not_advance_visible_generation` | function |  |
| `tests/test_repository_index.py::test_valid_source_without_symbols_is_not_treated_as_parse_failure` | function |  |
| `tests/test_repository_index.py::test_tree_sitter_syntax_error_is_rejected` | function |  |
| `tests/test_repository_index.py::test_typescript_import_type_array_in_generic_publishes` | function |  |
| `tests/test_repository_index.py::test_tsx_typeof_import_in_zero_arg_generic_publishes` | function |  |
| `tests/test_repository_index.py::test_modern_typescript_type_only_syntax_publishes` | function |  |
| `tests/test_repository_index.py::test_typescript_import_type_repair_does_not_hide_other_errors` | function |  |
| `tests/test_repository_index.py::test_transaction_failure_rolls_back_materialized_state` | function |  |
| `tests/test_repository_index.py::fail_relations` | function |  |
| `tests/test_repository_index.py::test_search_combines_exact_and_fts_and_separates_related_symbols` | function |  |
| `tests/test_repository_index.py::test_branch_scope_is_explicit_and_results_do_not_leak` | function |  |
| `tests/test_repository_index.py::test_repository_index_quality_gate_uses_real_git_corpus` | function |  |
| `tests/test_repository_index.py::test_enrichment_revision_is_atomic_and_enables_dense_recall` | function |  |
| `tests/test_repository_index.py::test_failed_enrichment_keeps_structural_generation_searchable` | function |  |
| `tests/test_repository_index.py::test_incremental_enrichment_embeds_only_changed_content` | function |  |
| `tests/test_repository_index.py::test_cross_branch_enrichment_reuses_content_addressed_vectors` | function |  |
| `tests/test_repository_index.py::test_enrichment_is_idempotent_for_published_model_and_generation` | function |  |
| `tests/test_repository_index.py::test_dense_query_failure_degrades_preferred_and_fails_required` | function |  |
| `tests/test_repository_index.py::test_sync_collects_old_generations_and_orphan_artifacts` | function |  |
| `tests/test_repository_index.py::test_maintenance_recovers_interrupted_current_enrichment` | function |  |
| `tests/test_repository_index.py::test_integrity_reports_foreign_key_violations` | function |  |
| `tests/test_runtime_safety.py::test_task_store_returns_copies_and_keeps_running_tasks_during_cleanup` | function |  |
| `tests/test_runtime_safety.py::test_registry_update_and_unregister_are_self_contained` | function |  |
| `tests/test_runtime_safety.py::test_source_context_rejects_path_escape` | function |  |
| `tests/test_runtime_safety.py::test_register_rejects_invalid_url_before_background_work` | function |  |
| `tests/test_runtime_safety.py::test_pre_commit_hook_uses_atomic_local_generation_command` | function |  |
| `tests/test_wiki.py::_make_node` | function |  |
| `tests/test_wiki.py::test_build_page_contains_symbol` | function |  |
| `tests/test_wiki.py::test_build_page_contains_calls` | function |  |
| `tests/test_wiki.py::test_build_page_contains_called_by` | function |  |
| `tests/test_wiki.py::test_build_page_no_agent_hints` | function |  |
| `tests/test_wiki.py::test_build_index_contains_page` | function |  |
| `tests/test_wiki.py::test_write_page_creates_file` | function |  |
## Relationships
- **Calls:** indexer/agent_context.py::locate_from_error, indexer/agent_contracts.py::agent_capabilities_manifest, indexer/agent_diagnostics.py::diagnose_index, indexer/agent_diff.py::change_set, indexer/agent_diff.py::coverage_map, indexer/agent_diff.py::index_diff_report, indexer/agent_diff.py::post_edit_verify, indexer/ast_parser.py::ASTNode, indexer/ast_parser.py::parse_file, indexer/cli.py::maintain, indexer/cli.py::run, indexer/config.py::Config, indexer/config.py::load_config, indexer/config.py::save_config, indexer/grouper.py::density_group, indexer/hooks.py::install_hook, indexer/repo_registry.py::RepoRegistry, indexer/repo_registry.py::RepoRegistry.get, indexer/repo_registry.py::RepoRegistry.items, indexer/repo_registry.py::RepoRegistry.register, indexer/repo_registry.py::RepoRegistry.unregister, indexer/repo_registry.py::RepoRegistry.update_meta, indexer/repository_benchmarks.py::run_repository_index_benchmark, indexer/repository_index.py::IndexScope, indexer/repository_index.py::RepositoryIndex, indexer/repository_index.py::RepositoryIndex.enrich, indexer/repository_index.py::RepositoryIndex.inspect, indexer/repository_index.py::RepositoryIndex.integrity, indexer/repository_index.py::RepositoryIndex.maintain, indexer/repository_index.py::RepositoryIndex.search, indexer/repository_index.py::RepositoryIndex.symbols, indexer/repository_index.py::RepositoryIndex.sync, indexer/repository_index.py::RepositoryIndex.trace, indexer/repository_index.py::SearchRequest, indexer/repository_index.py::SyncRequest, indexer/repository_projection.py::write_repository_projection, indexer/repository_service.py::RepositoryService, indexer/repository_service.py::RepositoryService.inspect, indexer/repository_service.py::RepositoryService.project, indexer/repository_service.py::RepositoryService.search, indexer/repository_service.py::RepositoryService.sync, indexer/repository_service.py::RepositoryService.trace, indexer/repository_service.py::resolve_revision, indexer/repository_store.py::RepositoryStore.connect, indexer/rest_api.py::change_set, indexer/rest_api.py::coverage_map, indexer/rest_api.py::create_app, indexer/rest_api.py::diagnose_index, indexer/rest_api.py::find_tests_for_symbol, indexer/rest_api.py::get_edit_context, indexer/rest_api.py::get_source_context, indexer/rest_api.py::index_diff_report, indexer/rest_api.py::locate_from_error, indexer/rest_api.py::post_edit_verify, indexer/retrieval.py::agent_capabilities_manifest, indexer/retrieval.py::agent_protocol_bundle, indexer/retrieval.py::change_set, indexer/retrieval.py::coverage_map, indexer/retrieval.py::diagnose_index, indexer/retrieval.py::find_tests_for_symbol, indexer/retrieval.py::get_edit_context, indexer/retrieval.py::get_source_context, indexer/retrieval.py::index_diff_report, indexer/retrieval.py::locate_from_error, indexer/retrieval.py::post_edit_verify, indexer/retrieval.py::search_code, indexer/search_eval.py::SearchCase, indexer/search_eval.py::evaluate_search, indexer/task_store.py::TaskStore, indexer/task_store.py::TaskStore._cleanup, indexer/task_store.py::TaskStore.create, indexer/task_store.py::TaskStore.get, indexer/task_store.py::TaskStore.update, indexer/wiki.py::IndexEntry, indexer/wiki.py::PageContext, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::write_page, tests/test_config.py::_clean_env, tests/test_config.py::_restore_env, tests/test_repository_adapters.py::_commit, tests/test_repository_adapters.py::_git, tests/test_repository_adapters.py::_registered_rest_repo, tests/test_repository_adapters.py::_repository, tests/test_repository_index.py::FakeEmbeddingProvider, tests/test_repository_index.py::FakeEmbeddingProvider._vector, tests/test_repository_index.py::_commit, tests/test_repository_index.py::_git, tests/test_repository_index.py::_index, tests/test_repository_index.py::_write_repository, tests/test_wiki.py::_make_node
- **Called by:** tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_repository_adapters.py::_commit, tests/test_repository_adapters.py::_repository, tests/test_repository_adapters.py::test_agent_context_and_diagnostics_read_repository_generation, tests/test_repository_adapters.py::test_branch_status_isolated_in_same_database, tests/test_repository_adapters.py::test_remote_tracking_ref_wins_over_stale_local_branch, tests/test_repository_adapters.py::test_rest_local_repo_uses_current_branch_when_registry_has_no_branch, tests/test_repository_adapters.py::test_rest_search_requires_explicit_branch_and_preserves_scope, tests/test_repository_adapters.py::test_rest_trace_rejects_unknown_branch, tests/test_repository_adapters.py::test_retrieval_and_service_return_the_same_generation_and_order, tests/test_repository_adapters.py::test_update_repo_and_sync_discovers_branch_with_repo_credentials, tests/test_repository_adapters.py::test_update_repo_and_sync_rejects_unmatched_rule_without_syncing_old_branches, tests/test_repository_index.py::FakeEmbeddingProvider.embed_documents, tests/test_repository_index.py::FakeEmbeddingProvider.embed_query, tests/test_repository_index.py::_commit, tests/test_repository_index.py::_write_repository, tests/test_repository_index.py::test_blob_artifact_survives_rename_without_stale_component_ids, tests/test_repository_index.py::test_branch_scope_is_explicit_and_results_do_not_leak, tests/test_repository_index.py::test_cli_run_and_status_use_repository_generation, tests/test_repository_index.py::test_cross_branch_enrichment_reuses_content_addressed_vectors, tests/test_repository_index.py::test_dense_query_failure_degrades_preferred_and_fails_required, tests/test_repository_index.py::test_enrichment_is_idempotent_for_published_model_and_generation, tests/test_repository_index.py::test_enrichment_revision_is_atomic_and_enables_dense_recall, tests/test_repository_index.py::test_failed_enrichment_keeps_structural_generation_searchable, tests/test_repository_index.py::test_incremental_enrichment_embeds_only_changed_content, tests/test_repository_index.py::test_incremental_sync_updates_and_removes_only_changed_paths, tests/test_repository_index.py::test_integrity_reports_foreign_key_violations, tests/test_repository_index.py::test_maintenance_recovers_interrupted_current_enrichment, tests/test_repository_index.py::test_modern_typescript_type_only_syntax_publishes, tests/test_repository_index.py::test_non_source_tree_change_publishes_snapshot_without_parsing, tests/test_repository_index.py::test_parse_failure_does_not_advance_visible_generation, tests/test_repository_index.py::test_repository_index_quality_gate_uses_real_git_corpus, tests/test_repository_index.py::test_same_blob_is_parsed_once_across_branches, tests/test_repository_index.py::test_search_combines_exact_and_fts_and_separates_related_symbols, tests/test_repository_index.py::test_staged_revision_captures_index_without_changing_git_state, tests/test_repository_index.py::test_symbols_project_current_generation_with_resolved_relations, tests/test_repository_index.py::test_sync_collects_old_generations_and_orphan_artifacts, tests/test_repository_index.py::test_sync_publishes_generation_and_inspect_reports_same_snapshot, tests/test_repository_index.py::test_trace_reads_current_generation_call_graph_in_both_directions, tests/test_repository_index.py::test_transaction_failure_rolls_back_materialized_state, tests/test_repository_index.py::test_tree_sitter_syntax_error_is_rejected, tests/test_repository_index.py::test_tsx_typeof_import_in_zero_arg_generic_publishes, tests/test_repository_index.py::test_typescript_import_type_array_in_generic_publishes, tests/test_repository_index.py::test_typescript_import_type_repair_does_not_hide_other_errors, tests/test_repository_index.py::test_unchanged_tree_is_constant_work_and_does_not_parse, tests/test_repository_index.py::test_valid_source_without_symbols_is_not_treated_as_parse_failure, tests/test_repository_index.py::test_wiki_projection_is_rendered_from_published_generation, tests/test_repository_index.py::test_worktree_revision_captures_unstaged_and_untracked_without_staging, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, click.testing.CliRunner, indexer.agent_context, indexer.agent_diagnostics, indexer.agent_diff, indexer.agent_graph, indexer.agent_protocol, indexer.ast_parser.ASTNode, indexer.ast_parser.parse_file, indexer.cli.main, indexer.config.Config, indexer.config.load_config, indexer.config.save_config, indexer.git_snapshot.STAGED_REVISION, indexer.git_snapshot.WORKTREE_REVISION, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.repo_registry.RepoRegistry, indexer.repository_benchmarks.run_repository_index_benchmark, indexer.repository_index.IndexScope, indexer.repository_index.RepositoryIndex, indexer.repository_index.RepositoryIndexError, indexer.repository_index.SearchRequest, indexer.repository_index.SyncRequest, indexer.repository_projection.write_repository_projection, indexer.repository_service.RepositoryService, indexer.repository_service.resolve_revision, indexer.rest_api, indexer.rest_api.create_app, indexer.retrieval.agent_capabilities_manifest, indexer.retrieval.agent_protocol_bundle, indexer.retrieval.change_set, indexer.retrieval.coverage_map, indexer.retrieval.diagnose_index, indexer.retrieval.find_tests_for_symbol, indexer.retrieval.get_edit_context, indexer.retrieval.get_source_context, indexer.retrieval.index_diff_report, indexer.retrieval.locate_from_error, indexer.retrieval.post_edit_verify, indexer.retrieval.search_code, indexer.search_eval.SearchCase, indexer.search_eval.evaluate_search, indexer.task_store.TaskStore, indexer.utils, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, inspect, os, pathlib.Path, pytest, sqlite3, starlette.testclient.TestClient, subprocess, tempfile, threading, time
## Entry Points
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
- `test_parse_returns_nodes`
- `test_function_node`
- `test_method_node`
- `test_class_node`
- `test_docstring_extracted`
- `test_imports_extracted`
- `test_calls_extracted`
- `test_python_fastapi_route_entry_point`
- `test_python_click_command_entry_point`
- `test_typescript_import_type_array_in_generic_preserves_structure`
- `test_typescript_import_types_in_generic_calls_preserve_structure`
- `test_typescript_runtime_dynamic_import_is_not_normalized`
- `test_tsx_typeof_import_in_zero_arg_generic_call_is_valid`
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
- `test_repository_index_generation_cost_scales_with_delta`
- `test_retrieval_and_service_return_the_same_generation_and_order`
- `test_rest_search_requires_explicit_branch_and_preserves_scope`
- `test_rest_local_repo_uses_current_branch_when_registry_has_no_branch`
- `test_rest_trace_rejects_unknown_branch`
- `test_update_repo_and_sync_discovers_branch_with_repo_credentials`
- `discover`
- `run_all`
- `test_update_repo_and_sync_rejects_unmatched_rule_without_syncing_old_branches`
- `test_agent_context_and_diagnostics_read_repository_generation`
- `test_branch_status_isolated_in_same_database`
- `test_remote_tracking_ref_wins_over_stale_local_branch`
- `test_sync_publishes_generation_and_inspect_reports_same_snapshot`
- `test_symbols_project_current_generation_with_resolved_relations`
- `test_trace_reads_current_generation_call_graph_in_both_directions`
- `test_wiki_projection_is_rendered_from_published_generation`
- `test_cli_run_and_status_use_repository_generation`
- `test_unchanged_tree_is_constant_work_and_does_not_parse`
- `unexpected_parse`
- `test_incremental_sync_updates_and_removes_only_changed_paths`
- `test_same_blob_is_parsed_once_across_branches`
- `test_blob_artifact_survives_rename_without_stale_component_ids`
- `test_non_source_tree_change_publishes_snapshot_without_parsing`
- `test_staged_revision_captures_index_without_changing_git_state`
- `test_worktree_revision_captures_unstaged_and_untracked_without_staging`
- `test_parse_failure_does_not_advance_visible_generation`
- `test_valid_source_without_symbols_is_not_treated_as_parse_failure`
- `test_tree_sitter_syntax_error_is_rejected`
- `test_typescript_import_type_array_in_generic_publishes`
- `test_tsx_typeof_import_in_zero_arg_generic_publishes`
- `test_modern_typescript_type_only_syntax_publishes`
- `test_typescript_import_type_repair_does_not_hide_other_errors`
- `test_transaction_failure_rolls_back_materialized_state`
- `fail_relations`
- `test_search_combines_exact_and_fts_and_separates_related_symbols`
- `test_branch_scope_is_explicit_and_results_do_not_leak`
- `test_repository_index_quality_gate_uses_real_git_corpus`
- `test_enrichment_revision_is_atomic_and_enables_dense_recall`
- `test_failed_enrichment_keeps_structural_generation_searchable`
- `test_incremental_enrichment_embeds_only_changed_content`
- `test_cross_branch_enrichment_reuses_content_addressed_vectors`
- `test_enrichment_is_idempotent_for_published_model_and_generation`
- `test_dense_query_failure_degrades_preferred_and_fails_required`
- `test_sync_collects_old_generations_and_orphan_artifacts`
- `test_maintenance_recovers_interrupted_current_enrichment`
- `test_integrity_reports_foreign_key_violations`
- `test_task_store_returns_copies_and_keeps_running_tasks_during_cleanup`
- `test_registry_update_and_unregister_are_self_contained`
- `test_source_context_rejects_path_escape`
- `test_register_rejects_invalid_url_before_background_work`
- `test_pre_commit_hook_uses_atomic_local_generation_command`
- `test_build_page_contains_symbol`
- `test_build_page_contains_calls`
- `test_build_page_contains_called_by`
- `test_build_page_no_agent_hints`
- `test_build_index_contains_page`
- `test_write_page_creates_file`
