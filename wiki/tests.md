# tests/

## Overview

The `test_ast_parser.py` module validates the core `ast_parser` (likely in `ast_parser.py`), which converts source files of multiple languages (Python, Rust, Java, Ruby) into a structured list of node objects. Each node captures type (e.g., function, class, method), name, docstring, imports, and call references. This parser is foundational for downstream code analysis and caching layers; tests ensure correctness across languages and edge cases like trait methods, type aliases, and javadoc extraction. Cache roundtrip tests verify that parsed nodes can be persisted and reloaded identically, which is critical for incremental analysis. These tests are part of CI and must pass before any parser changes are merged.

## Modules
| File | Purpose |
|------|---------|
| tests/test_p1_fixes.py | Regression tests for bug fixes and edge cases |
| tests/test_ast_parser.py | Unit tests for AST parser module |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function | Asserts that parsed file yields non-empty node list |
| `tests/test_ast_parser.py::test_function_node` | function | Asserts that parsed AST contains a function node |
| `tests/test_ast_parser.py::test_method_node` | function | Asserts that parsed AST contains a method node |
| `tests/test_ast_parser.py::test_class_node` | function | Asserts that parsed AST contains a class node |
| `tests/test_ast_parser.py::test_docstring_extracted` | function | Asserts that parsed node has expected docstring |
| `tests/test_ast_parser.py::test_imports_extracted` | function | Asserts that parsed node contains imports list |
| `tests/test_ast_parser.py::test_calls_extracted` | function | Asserts that parsed node contains calls list |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function | Tests that nodes can be saved and loaded from cache |
| `tests/test_ast_parser.py::test_rust_parse_returns_nodes` | function | Asserts Rust file parse returns non-empty nodes |
| `tests/test_ast_parser.py::test_rust_function_node` | function | Asserts Rust AST contains a function node |
| `tests/test_ast_parser.py::test_rust_struct_node` | function | Asserts Rust AST contains a struct node |
| `tests/test_ast_parser.py::test_rust_method_node` | function | Asserts Rust AST contains a method node |
| `tests/test_ast_parser.py::test_rust_trait_node` | function | Asserts Rust AST contains a trait node |
| `tests/test_ast_parser.py::test_rust_trait_method_spec` | function | Asserts Rust AST contains a trait method signature |
| `tests/test_ast_parser.py::test_rust_enum_node` | function | Asserts Rust AST contains an enum node |
| `tests/test_ast_parser.py::test_rust_type_alias` | function | Asserts Rust AST contains a type alias node |
| `tests/test_ast_parser.py::test_rust_docstring_extracted` | function | Asserts Rust node docstring is extracted |
| `tests/test_ast_parser.py::test_rust_imports_extracted` | function | Asserts Rust node imports are extracted |
| `tests/test_ast_parser.py::test_java_parse_returns_nodes` | function | Asserts Java file parse returns non-empty nodes |
| `tests/test_ast_parser.py::test_java_class_node` | function | Asserts Java AST contains a class node |
| `tests/test_ast_parser.py::test_java_method_node` | function | Asserts Java AST contains a method node |
| `tests/test_ast_parser.py::test_java_interface_node` | function | Asserts Java AST contains an interface node |
| `tests/test_ast_parser.py::test_java_enum_node` | function | Asserts Java AST contains an enum node |
| `tests/test_ast_parser.py::test_java_javadoc_extracted` | function | Asserts Java node javadoc is extracted |
| `tests/test_ast_parser.py::test_java_imports_extracted` | function | Asserts Java node imports are extracted |
| `tests/test_ast_parser.py::test_ruby_parse_returns_nodes` | function | Asserts Ruby file parse returns non-empty nodes |
| `tests/test_ast_parser.py::test_ruby_class_node` | function | Asserts Ruby AST contains a class node |
| `tests/test_ast_parser.py::test_ruby_method_node` | function | Asserts Ruby AST contains a method node |
| `tests/test_ast_parser.py::test_ruby_module_node` | function | Tests that parse_file finds a Ruby module node |
| `tests/test_ast_parser.py::test_ruby_function_node` | function | Tests that parse_file finds a Ruby function node |
| `tests/test_ast_parser.py::test_ruby_docstring_extracted` | function | Tests that parse_file extracts Ruby docstring text |
| `tests/test_p1_fixes.py::TestTaskStore` | class | Test suite for TaskStore CRUD and cleanup operations |
| `tests/test_p1_fixes.py::TestTaskStore.test_create_task` | method | Tests TaskStore.create stores and retrieves a new task |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_task` | method | Tests TaskStore.update modifies and retrieves an existing task |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_finished_sets_timestamp` | method | Tests TaskStore.update sets finished timestamp on completion |
| `tests/test_p1_fixes.py::TestTaskStore.test_update_nonexistent_task_noop` | method | Tests TaskStore.update on nonexistent task does nothing |
| `tests/test_p1_fixes.py::TestTaskStore.test_get_nonexistent_returns_none` | method | Tests TaskStore.get returns None for missing task |
| `tests/test_p1_fixes.py::TestTaskStore.test_cleanup_expired_tasks` | method | Tests TaskStore._cleanup removes expired tasks |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety` | class | Test suite for thread-safe RepoRegistry registration |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_register` | method | Tests concurrent RepoRegistry.register does not race |
| `tests/test_p1_fixes.py::TestRepoRegistryThreadSafety.test_concurrent_unregister` | method | Tests concurrent RepoRegistry.unregister does not race |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock` | class | Test suite for repo lock skip-lock behavior |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_skip_lock_does_not_release` | method | Tests skip lock acquisition does not release the lock |
| `tests/test_p1_fixes.py::TestRepoLockSkipLock.test_lock_blocks_concurrent` | method | Tests lock acquisition blocks concurrent access |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone` | class | Test suite for RepoRegistry.get returning None |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_nonexistent_returns_none` | method | Tests RepoRegistry.get returns None for unregistered repo |
| `tests/test_p1_fixes.py::TestRepoRegistryGetNone.test_get_returns_none_safely` | method | Tests RepoRegistry.get returns None without exception |
| `tests/test_p1_fixes.py::TestParseBody` | class | Test suite for _parse_body JSON parsing behavior |
| `tests/test_p1_fixes.py::TestParseBody.test_valid_json` | method | Tests _parse_body returns parsed JSON dict |
| `tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty` | method | Tests _parse_body returns {} on invalid JSON |
| `tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty` | method | Tests _parse_body returns {} when parsed value is not dict |
| `tests/test_p1_fixes.py::asyncio_coro` | function | Helper coroutine factory for async test mocks |
| `tests/test_p1_fixes.py::TestManifestFieldValidation` | class | Test suite for missing/corrupt manifest field handling |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_component_ids_defaults_empty` | method | Tests load_manifest defaults missing component_ids to [] |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_missing_hash_defaults_empty` | method | Tests load_manifest defaults missing hash to {} |
| `tests/test_p1_fixes.py::TestManifestFieldValidation.test_corrupt_manifest_returns_empty` | method | Tests load_manifest returns {} on corrupt JSON file |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString` | class | Test suite for _apply_env ignoring empty strings |
| `tests/test_p1_fixes.py::TestApplyEnvEmptyString.test_empty_string_does_not_override_default` | method | Tests _apply_env does not override config with empty env value |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck` | class | Test suite for git checkout failure handling |
| `tests/test_p1_fixes.py::TestGitReturnCodeCheck.test_git_checkout_failure_sets_task_failed` | method | Tests _run_rebuild_task_inner sets task failed on git error |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers` | class | Test suite for cross-reference caller merging |
| `tests/test_p1_fixes.py::TestCrossReferenceMergeCallers.test_cross_reference_merges_same_file_and_cross_file_callers` | method | Tests cross_reference merges callers from same and different files |
| `tests/test_p1_fixes.py::TestUpdateMetaLock` | class | Test suite for update_meta using repo lock |
| `tests/test_p1_fixes.py::TestUpdateMetaLock.test_update_meta_uses_lock` | method | Tests RepoRegistry.update_meta acquires repo lock |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping` | class | Test suite for env file quote stripping |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_double_quotes_stripped` | method | Tests load_env_file strips double quotes from env values |
| `tests/test_p1_fixes.py::TestEnvQuoteStripping.test_single_quotes_stripped` | method | Tests load_env_file strips single quotes from env values |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList` | class | Test suite for _truncate_list preserving valid JSON |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_truncate_produces_valid_json` | method | Tests _truncate_list returns valid JSON for large input |
| `tests/test_p1_fixes.py::TestVectorStoreTruncateList.test_small_list_not_truncated` | method | Tests _truncate_list leaves small input unchanged |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion` | class | Test suite for type coercion in get_source_context |
| `tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int` | method | Tests get_source_context converts string line/context to int |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock` | class | Test suite for lock cleanup on unregister |
| `tests/test_p1_fixes.py::TestUnregisterCleansLock.test_unregister_removes_repo_lock` | method | Tests RepoRegistry.unregister removes the repo lock file |
| `tests/test_p1_fixes.py::TestAtomicWrites` | class | Test suite for atomic file writes of config and manifest |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_config_atomic` | method | Tests Config.save_config writes atomically via temp file |
| `tests/test_p1_fixes.py::TestAtomicWrites.test_save_manifest_atomic` | method | Tests Manifest.save_manifest writes atomically via temp file |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause` | class | Test suite for single-branch WHERE clause in RepoRegistry.get |
| `tests/test_p1_fixes.py::TestSingleBranchWhereClause.test_single_branch_gets_where_clause` | method | Tests RepoRegistry.get with single branch returns filtered results |
| `tests/test_p1_fixes.py::TestIntParamValidation` | class | Test suite for integer parameter validation in get_source_context |
| `tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400` | method | Tests get_source_context returns 400 for invalid line_start |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy` | class | Test suite for webhook branch list immutability |
| `tests/test_p1_fixes.py::TestWebhookBranchCopy.test_webhook_branch_list_not_mutated` | method | Tests webhook branch list is not mutated by handler |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning` | class | Test suite for cleanup skipping running tasks |
| `tests/test_p1_fixes.py::TestCleanupSkipsRunning.test_cleanup_does_not_evict_running_tasks` | method | Tests TaskStore._cleanup does not remove running tasks |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse` | class | Test suite for embed_query raising on empty input |
| `tests/test_p1_fixes.py::TestEmbedQueryEmptyResponse.test_embed_query_raises_on_empty` | method | Tests EmbeddingConfig.embed_query raises on empty query |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone` | class | Test suite for compute_hash returning None on OSError |
| `tests/test_p1_fixes.py::TestComputeHashReturnsNone.test_compute_hash_returns_none_on_oserror` | method | Tests compute_hash returns None when file is inaccessible |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit` | class | Test suite for changed_files_since invalid commit |
| `tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit` | method | Tests changed_files_since raises on invalid commit hash |
| `tests/test_p1_fixes.py::TestExpansionCap` | class | Test suite for expansion cap in _expand_with_call_graph |
| `tests/test_p1_fixes.py::TestExpansionCap.test_expand_with_call_graph_respects_max` | method | Tests _expand_with_call_graph respects expansion limit |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion` | class | Test suite for expansion cap with patched function |
| `tests/test_p1_fixes.py::TestExpansionCapWithExpansion.test_expand_caps_at_max` | method | Tests _expand_with_call_graph caps at max expansions |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape` | class | Test suite for XSS escaping of API keys |
| `tests/test_p1_fixes.py::TestXSSApiKeyEscape.test_api_key_script_tag_escaped` | method | Tests that script tags in API key are replaced |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive` | class | Test suite for case-insensitive Bearer token |
| `tests/test_p1_fixes.py::TestBearerCaseInsensitive.test_lowercase_bearer_accepted` | method | Tests lowercase bearer prefix is accepted |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK` | class | Test suite for CJK character token budget triple |
| `tests/test_p1_fixes.py::TestBatchTokenEstimateCJK.test_char_budget_uses_triple` | method | Tests build_batches triples token budget for CJK nodes |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock` | class | Test suite for reentrant lock avoiding deadlock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_register_repo_no_deadlock` | method | Tests RepoRegistry registration with RLock does not deadlock |
| `tests/test_p1_fixes.py::TestRLockNoDeadlock.test_rlock_allows_reentrant` | method | Tests RLock.acquire works reentrantly |
| `tests/test_p1_fixes.py::TestTopKNegativeValue` | class | Test suite for clamping negative top_k to 1 |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_negative_clamped_to_one` | method | Tests negative top_k clamped to 1 via min/max |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_zero_clamped_to_one` | method | Tests zero top_k clamped to 1 via min/max |
| `tests/test_p1_fixes.py::TestTopKNegativeValue.test_top_k_normal_value` | method | Tests normal top_k passed through unchanged |
| `tests/test_p1_fixes.py::TestEmbeddingRetry` | class | Test suite for retry logic in embedding API call |
| `tests/test_p1_fixes.py::TestEmbeddingRetry.test_call_embedding_api_has_retry` | method | Tests that call_embedding_api includes retry decorator |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection` | class | Test suite for custom error on empty LLM choices |
| `tests/test_p1_fixes.py::TestEmptyChoicesProtection.test_litellm_empty_choices_raises_custom_error` | method | Tests empty litellm choices raise custom exception |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes` | class | Test suite for vector store stale method using all node ids |
| `tests/test_p1_fixes.py::TestVectorStoreStaleByAllNodes.test_stale_uses_all_node_ids` | method | Tests stale method checks all stored node IDs |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet` | class | Test suite for branch always in vector store metadata |
| `tests/test_p1_fixes.py::TestVectorStoreBranchAlwaysSet.test_branch_always_in_metadata` | method | Tests that branch field is always present in metadata |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd` | class | Test suite for discover_remote_branches cwd parameter |
| `tests/test_p1_fixes.py::TestDiscoverRemoteBranchesCwd.test_discover_has_cwd_param` | method | Tests discover_remote_branches accepts a cwd argument |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite` | class | Test suite for atomic credential file writing |
| `tests/test_p1_fixes.py::TestCredentialAtomicWrite.test_credential_write_uses_tmp` | method | Tests credential writes use a temporary file |
| `tests/test_p1_fixes.py::TestConfigValidation` | class | Test suite for config field validation and reset |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_max_tokens_per_batch_reset` | method | Tests Config resets invalid max_tokens_per_batch to default |
| `tests/test_p1_fixes.py::TestConfigValidation.test_invalid_dimensions_reset` | method | Tests Config resets invalid dimensions to default |
| `tests/test_p1_fixes.py::TestRubyModuleMethod` | class | Test suite for Ruby module method naming |
| `tests/test_p1_fixes.py::TestRubyModuleMethod.test_module_method_has_prefix` | method | Tests Ruby module method gets ClassName prefix |
| `tests/test_p1_fixes.py::_coro` | function |  |
| `tests/test_p1_fixes.py::run` | function | Test helper that calls _parse_body or get_source_context with mocks |
| `tests/test_p1_fixes.py::run` | function | Test helper that calls _parse_body or get_source_context with mocks |
| `tests/test_p1_fixes.py::run` | function | Test helper that calls _parse_body or get_source_context with mocks |
| `tests/test_p1_fixes.py::run` | function | Test helper that calls _parse_body or get_source_context with mocks |
| `tests/test_p1_fixes.py::run` | function | Test helper that calls _parse_body or get_source_context with mocks |
| `tests/test_p1_fixes.py::register_repo` | function | Test helper that registers a repo via RepoRegistry |
| `tests/test_p1_fixes.py::unregister_repo` | function | Test helper that unregisters a repo from RepoRegistry |
## Data Flows
- Test calls parse_file on a Python fixture → receives node list → asserts length > 0 and specific node attributes (name, type, docstring, imports, calls).
- Test parses a Rust fixture → verifies presence of function, struct, method, trait, trait method spec, enum, type alias nodes and extracts docstrings and imports.
- Test parses a Java fixture → checks class, method, interface, enum nodes; validates javadoc extraction and import list.
- Cache flow: parse_file → save_cached_nodes to a temporary directory → load_cached_nodes → assert node count matches original.
## Design Constraints
- Language detection is based on file extension; parsing a file with an unsupported extension may return an empty list (this is untested here but implied by the fixture-only approach).
- Cache serialization uses temporary directories; nodes must be JSON-serializable or picklable; the test only compares length, not deep equality.
- Docstring extraction heuristics differ per language: Python uses triple-quoted strings, Rust uses `///` comments, Java uses `/** */` blocks, Ruby uses `=begin`/`=end` or `#` comments—tests assert extraction for each.
- Import extraction returns a list of strings; for Java it includes package declarations, for Rust `use` statements, for Python `import`/`from`, for Ruby `require`/`include`—tested via `isinstance` and `len`.
- Node identity checks rely on `any` and `endswith` for name matching, implying nodes have a `.name` attribute that includes a type suffix or exact filename-derived name.
- The parser must handle multi-language files (e.g., Rust traits with method signatures, Ruby modules) consistently; tests for Rust trait method specs confirm that empty-bodies or signatures are still parsed as nodes.
## Relationships
- **Calls:** ASTNode, Config, EmbeddingConfig, Exception, MagicMock, Manifest, Path, RLock, RepoRegistry, TaskStore, TemporaryDirectory, Thread, __import__, _apply_env, _cleanup, _coro, _expand_with_call_graph, _get_repo_lock, _parse_body, _run_rebuild_task_inner, _truncate_list, acquire, any, append, asyncio_coro, build_batches, changed_files_since, compare_digest, compute_hash, create, cross_reference, dict, dumps, embed_query, endswith, exists, get, get_source_context, getsource, isinstance, join, len, list, load_cached_nodes, load_config, load_env_file, load_manifest, loads, lower, max, min, mkdir, mkdtemp, next, object, parse_file, parse_ruby_file, patch, pop, range, read_text, register, release, replace, run, save_cached_nodes, save_config, save_manifest, signature, start, startswith, str, time, unregister, update, update_meta, write_text
- **Called by:** indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/git.py::_run, indexer/git.py::changed_files_since, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_discover_remote_branches, indexer/rest_api.py::_run_rebuild_task_inner, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::list_repos, indexer/rest_api.py::repo_detail, tests/test_p1_fixes.py::TestChangedFilesSinceInvalidCommit.test_raises_on_invalid_commit, tests/test_p1_fixes.py::TestGetSourceContextTypeCoercion.test_string_params_converted_to_int, tests/test_p1_fixes.py::TestIntParamValidation.test_invalid_line_start_returns_400, tests/test_p1_fixes.py::TestParseBody.test_invalid_json_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_non_dict_returns_empty, tests/test_p1_fixes.py::TestParseBody.test_valid_json, tests/test_p1_fixes.py::asyncio_coro
- **Imports from:** asyncio, hmac, indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config._apply_env, indexer.config.load_config, indexer.config.save_config, indexer.embedding._call_embedding_api, indexer.embedding.embed_query, indexer.git.changed_files_since, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.llm._litellm_completion, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.rest_api.RepoRegistry, indexer.rest_api.TaskStore, indexer.rest_api._InvalidBodyError, indexer.rest_api._discover_remote_branches, indexer.rest_api._get_repo_lock, indexer.rest_api._locks_lock, indexer.rest_api._parse_body, indexer.rest_api._repo_locks, indexer.rest_api._run_rebuild_task_inner, indexer.rest_api._store_credentials, indexer.rest_api.get_source_context, indexer.rest_api.tasks, indexer.retrieval._expand_with_call_graph, indexer.retrieval._parse_json_list, indexer.ruby_parser.parse_ruby_file, indexer.utils, indexer.utils._env_loaded, indexer.utils.load_env_file, indexer.vector_store._build_meta, indexer.vector_store._truncate_list, indexer.vector_store.upsert_nodes, inspect, json, os, pathlib.Path, subprocess, tempfile, threading, time, unittest.mock.MagicMock, unittest.mock.patch
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
- `register_repo`
- `unregister_repo`
