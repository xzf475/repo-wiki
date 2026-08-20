# indexer/

## Modules
| File | Purpose |
|------|---------|
| indexer/__init__.py |  |
| indexer/agent_context.py |  |
| indexer/agent_contracts.py |  |
| indexer/agent_diagnostics.py |  |
| indexer/agent_diff.py |  |
| indexer/agent_graph.py |  |
| indexer/agent_protocol.py |  |
| indexer/ast_parser.py |  |
| indexer/cli.py |  |
| indexer/config.py |  |
| indexer/embedding.py |  |
| indexer/git.py |  |
| indexer/git_ops.py |  |
| indexer/git_snapshot.py |  |
| indexer/go_parser.py |  |
| indexer/grouper.py |  |
| indexer/hooks.py |  |
| indexer/java_parser.py |  |
| indexer/js_parser.py |  |
| indexer/mcp_server.py |  |
| indexer/repo_registry.py |  |
| indexer/repository_benchmarks.py |  |
| indexer/repository_embedding.py |  |
| indexer/repository_index.py |  |
| indexer/repository_projection.py |  |
| indexer/repository_service.py |  |
| indexer/repository_store.py |  |
| indexer/rest_api.py |  |
| indexer/retrieval.py |  |
| indexer/ruby_parser.py |  |
| indexer/rust_parser.py |  |
| indexer/search_eval.py |  |
| indexer/task_store.py |  |
| indexer/utils.py |  |
| indexer/wiki.py |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/agent_context.py::resolve_symbol` | function |  |
| `indexer/agent_context.py::impact_analysis` | function |  |
| `indexer/agent_context.py::change_plan` | function |  |
| `indexer/agent_context.py::list_entry_points` | function |  |
| `indexer/agent_context.py::locate_from_error` | function |  |
| `indexer/agent_contracts.py::agent_capabilities_manifest` | function |  |
| `indexer/agent_contracts.py::agent_schema` | function |  |
| `indexer/agent_contracts.py::_capability_input_schema` | function |  |
| `indexer/agent_contracts.py::_capability_required_output` | function |  |
| `indexer/agent_contracts.py::_capability_example` | function |  |
| `indexer/agent_contracts.py::_capability_next_tools` | function |  |
| `indexer/agent_contracts.py::_object_schema` | function |  |
| `indexer/agent_contracts.py::_field_schema` | function |  |
| `indexer/agent_contracts.py::_agent_json_schema` | function |  |
| `indexer/agent_contracts.py::_endpoint_specs` | function |  |
| `indexer/agent_diagnostics.py::diagnose_index` | function |  |
| `indexer/agent_diff.py::post_edit_verify` | function |  |
| `indexer/agent_diff.py::stable_symbol_id` | function |  |
| `indexer/agent_diff.py::change_set` | function |  |
| `indexer/agent_diff.py::coverage_map` | function |  |
| `indexer/agent_diff.py::index_diff_report` | function |  |
| `indexer/agent_graph.py::cross_repo_graph` | function |  |
| `indexer/ast_parser.py::ASTNode` | class |  |
| `indexer/ast_parser.py::_extract_imports` | function |  |
| `indexer/ast_parser.py::_extract_calls` | function |  |
| `indexer/ast_parser.py::_get_class_method_ids` | function |  |
| `indexer/ast_parser.py::_entry_point_from_decorators` | function |  |
| `indexer/ast_parser.py::_attach_source` | function | Attach the exact source span to parser results from every language. |
| `indexer/ast_parser.py::parse_file` | function |  |
| `indexer/cli.py::main` | function |  |
| `indexer/cli.py::init` | function | Create .indexer.toml, install pre-commit hook, append to CLAUDE.md. |
| `indexer/cli.py::run` | function | Index the codebase and generate wiki pages. |
| `indexer/cli.py::status` | function | Show the current generation and workspace freshness. |
| `indexer/cli.py::maintain` | function | Recover interrupted jobs, collect unreachable state, and verify SQLite. |
| `indexer/cli.py::agent` | function | Run local Agent code-location workflows. |
| `indexer/cli.py::agent_context` | function | Print an edit-context bundle for a symbol. |
| `indexer/cli.py::agent_verify` | function | Suggest verification after an Agent edit. |
| `indexer/cli.py::agent_plan` | function | Print an Agent change plan. |
| `indexer/cli.py::agent_diagnose` | function | Print local index health diagnostics. |
| `indexer/cli.py::agent_capabilities` | function | Print the Agent tool manifest. |
| `indexer/cli.py::agent_schema` | function | Print the machine-readable Agent API schema. |
| `indexer/cli.py::hook` | function | Manage the pre-commit hook. |
| `indexer/cli.py::hook_install` | function | Install the pre-commit hook in the current repo. |
| `indexer/cli.py::hook_remove` | function | Remove the pre-commit hook from the current repo. |
| `indexer/cli.py::serve` | function | Start the repo-wiki MCP server for semantic code search. |
| `indexer/cli.py::serve_api` | function | Start a REST API server for remote semantic code search across multiple repos. |
| `indexer/cli.py::_ensure_cache_gitignore` | function |  |
| `indexer/cli.py::_json_dumps` | function |  |
| `indexer/config.py::EmbeddingConfig` | class |  |
| `indexer/config.py::Config` | class |  |
| `indexer/config.py::_env` | function |  |
| `indexer/config.py::_apply_env_field` | function |  |
| `indexer/config.py::_env_int` | function |  |
| `indexer/config.py::load_config` | function |  |
| `indexer/config.py::_apply_env` | function |  |
| `indexer/config.py::save_config` | function |  |
| `indexer/embedding.py::_get_openai_client` | function |  |
| `indexer/embedding.py::_resolve_api_key` | function |  |
| `indexer/embedding.py::embed_texts` | function | Embed an ordered batch atomically; any failed sub-batch raises. |
| `indexer/embedding.py::embed_query` | function |  |
| `indexer/embedding.py::_call_embedding_api` | function |  |
| `indexer/git.py::_run` | function |  |
| `indexer/git.py::current_branch` | function |  |
| `indexer/git.py::is_git_repo` | function |  |
| `indexer/git_ops.py::GitOperationError` | class |  |
| `indexer/git_ops.py::GitOperationError.__init__` | method |  |
| `indexer/git_ops.py::git_fetch_refs` | function | Refresh remote refs without changing or cleaning the active worktree. |
| `indexer/git_ops.py::git_fetch_checkout_pull` | function |  |
| `indexer/git_ops.py::_err` | function |  |
| `indexer/git_ops.py::_cleanup_worktree` | function |  |
| `indexer/git_ops.py::_detect_default_branch` | function |  |
| `indexer/git_ops.py::_match_branch_rule` | function |  |
| `indexer/git_ops.py::_discover_remote_branches` | function |  |
| `indexer/git_ops.py::_inject_credentials` | function |  |
| `indexer/git_ops.py::_sanitize_error` | function |  |
| `indexer/git_ops.py::_store_credentials` | function |  |
| `indexer/git_snapshot.py::GitSnapshotError` | class |  |
| `indexer/git_snapshot.py::TreeEntry` | class |  |
| `indexer/git_snapshot.py::TreeDelta` | class |  |
| `indexer/git_snapshot.py::GitSnapshot` | class | Read immutable Git trees without checking them out. |
| `indexer/git_snapshot.py::GitSnapshot.__init__` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.__enter__` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.__exit__` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.close` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.resolve_tree` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.initial_delta` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.delta` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.read_blobs` | method |  |
| `indexer/git_snapshot.py::GitSnapshot.prune_snapshots` | method | Remove loose synthetic objects unreachable from retained generations. |
| `indexer/git_snapshot.py::GitSnapshot._list_tree` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._entries_for_paths` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._run_text` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._capture_worktree_tree` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._capture_staged_tree` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._object_environment` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._remove_generated_paths` | method |  |
| `indexer/git_snapshot.py::GitSnapshot._run_bytes` | method |  |
| `indexer/git_snapshot.py::_is_indexable` | function |  |
| `indexer/go_parser.py::_get_go_language` | function |  |
| `indexer/go_parser.py::_extract_go_doc` | function |  |
| `indexer/go_parser.py::_extract_imports` | function |  |
| `indexer/go_parser.py::visit` | function |  |
| `indexer/go_parser.py::_extract_calls` | function |  |
| `indexer/go_parser.py::_get_receiver` | function |  |
| `indexer/go_parser.py::parse_go_file` | function |  |
| `indexer/grouper.py::density_group` | function |  |
| `indexer/grouper.py::folder_of` | function |  |
| `indexer/grouper.py::prefixes` | function |  |
| `indexer/grouper.py::resolve_group` | function |  |
| `indexer/hooks.py::_hook_command` | function |  |
| `indexer/hooks.py::_hook_script_fresh` | function |  |
| `indexer/hooks.py::_hook_script_append` | function |  |
| `indexer/hooks.py::install_hook` | function | Install or update the pre-commit hook.

- Fresh install: writes a new hook script
- Existing repo-wiki hook: updates the command in-place
- Existing non-repo-wiki hook: appends our block |
| `indexer/hooks.py::remove_hook` | function | Remove the repo-wiki-managed portion of the pre-commit hook. |
| `indexer/java_parser.py::_get_java_language` | function |  |
| `indexer/java_parser.py::_extract_javadoc` | function |  |
| `indexer/java_parser.py::_extract_imports` | function |  |
| `indexer/java_parser.py::visit` | function |  |
| `indexer/java_parser.py::_extract_calls` | function |  |
| `indexer/java_parser.py::parse_java_file` | function |  |
| `indexer/js_parser.py::_get_language` | function |  |
| `indexer/js_parser.py::_extract_jsdoc` | function |  |
| `indexer/js_parser.py::_extract_imports` | function |  |
| `indexer/js_parser.py::visit` | function |  |
| `indexer/js_parser.py::_extract_calls` | function |  |
| `indexer/js_parser.py::_walk_tree` | function |  |
| `indexer/js_parser.py::_import_type_expression` | function |  |
| `indexer/js_parser.py::_is_type_only_import` | function |  |
| `indexer/js_parser.py::_export_type_star_span` | function |  |
| `indexer/js_parser.py::_mask_span` | function |  |
| `indexer/js_parser.py::_normalize_typescript_tree` | function | Reparse known TypeScript grammar gaps without changing source offsets. |
| `indexer/js_parser.py::parse_js_file` | function |  |
| `indexer/mcp_server.py::_apply_mcp_auth` | function |  |
| `indexer/mcp_server.py::_patched_method` | function |  |
| `indexer/mcp_server.py::_MCPAuthMiddleware` | class |  |
| `indexer/mcp_server.py::_MCPAuthMiddleware.dispatch` | method |  |
| `indexer/mcp_server.py::create_server` | function |  |
| `indexer/mcp_server.py::search_symbols_tool` | function | Search code symbols by semantic query. Returns matching symbols with descriptions,
file locations, and optionally related symbols via call graph expansion.

Use this when: analyzing a bug report, finding code related to an error message,
locating where a feature is implemented, or understanding what a module does.

Args:
    query: Natural language description of what you're looking for (e.g. "JWT token validation", "database connection pool")
    top_k: Number of top results to return (default 10)
    expand_depth: How many hops in the call graph to expand (0=no expansion, 1=direct callers/callees)
    retrieval: local, preferred, or required dense retrieval |
| `indexer/mcp_server.py::trace_call_tool` | function |  |
| `indexer/mcp_server.py::get_source_context_tool` | function | Read source code context around specific lines. Returns the code with line numbers
and optional padding lines before/after the specified range.

Use this when: you need to see the actual implementation after locating a symbol via search or trace,
reviewing the exact code that needs to be modified for a bug fix, or understanding the
context around an error location.

Args:
    file_path: Repository-relative file path (e.g. "src/auth/token_validator.py")
    line_start: Start line number
    line_end: End line number
    padding: Extra lines to include before and after the range (default 5) |
| `indexer/mcp_server.py::get_edit_context_tool` | function | Return an edit-ready context bundle for a symbol: source, callers, callees,
sibling symbols, candidate tests, and index freshness.

Use this before modifying code after a symbol has been located. |
| `indexer/mcp_server.py::resolve_symbol_tool` | function | Resolve a natural language query or symbol name to a concrete component_id. |
| `indexer/mcp_server.py::find_tests_for_symbol_tool` | function | Find likely test files for a symbol based on indexed files, symbol names,
imports, and test naming conventions. |
| `indexer/mcp_server.py::pre_edit_check_tool` | function | Run pre-edit checks for a symbol: index freshness, dirty files, tests, commands, impact hints. |
| `indexer/mcp_server.py::impact_analysis_tool` | function | Analyze the likely impact of changing a symbol: callers, callees, tests,
entry points, affected files, risk points, and index freshness. |
| `indexer/mcp_server.py::change_plan_tool` | function | Create an agent-ready modification plan for a goal and target symbol. |
| `indexer/mcp_server.py::diagnose_index_tool` | function | Diagnose generation integrity, Wiki projection, source files, and freshness. |
| `indexer/mcp_server.py::agent_protocol_tool` | function | Return compact agent protocol fields: files to read, edit targets,
verification commands, warnings, and index freshness. |
| `indexer/mcp_server.py::locate_from_error_tool` | function | Locate likely code symbols from a stack trace, error log, HTTP path, or exception text. |
| `indexer/mcp_server.py::list_entry_points_tool` | function | List indexed API/CLI/event/job/webhook entry points. |
| `indexer/mcp_server.py::post_edit_verify_tool` | function | Verify local edits before commit. If diff is omitted, reads local git diff. |
| `indexer/mcp_server.py::change_set_tool` | function | Build a must-change set from a goal plus target symbol or diff. |
| `indexer/mcp_server.py::coverage_map_tool` | function | Map source symbols to likely covering tests. |
| `indexer/mcp_server.py::index_diff_report_tool` | function | Summarize symbol, entry point, and call graph changes between two index snapshots. |
| `indexer/mcp_server.py::cross_repo_graph_tool` | function | Local mode has one repo, so returns an empty cross-repo graph. |
| `indexer/mcp_server.py::agent_capabilities_manifest_tool` | function | Return tool capability manifest and recommended Agent flow. |
| `indexer/mcp_server.py::stable_symbol_id_tool` | function | Generate deterministic stable symbol id for rename/move tracking. |
| `indexer/mcp_server.py::get_index_status_tool` | function | Report whether the local index is stale relative to the current workspace. |
| `indexer/mcp_server.py::create_api_server` | function |  |
| `indexer/mcp_server.py::_api_request` | function |  |
| `indexer/mcp_server.py::_api_get` | function |  |
| `indexer/mcp_server.py::_api_post` | function |  |
| `indexer/mcp_server.py::list_repos` | function | List all registered repositories. Returns repo names, descriptions, tags, and basic stats.

Use this first to discover which repos are available before searching or tracing.
The description and tags help you understand which repo is relevant to the user's task. |
| `indexer/repo_registry.py::_get_repo_lock` | function |  |
| `indexer/repo_registry.py::RepoRegistry` | class |  |
| `indexer/repo_registry.py::RepoRegistry.__init__` | method |  |
| `indexer/repo_registry.py::RepoRegistry._save` | method |  |
| `indexer/repo_registry.py::RepoRegistry._load` | method |  |
| `indexer/repo_registry.py::RepoRegistry.register` | method |  |
| `indexer/repo_registry.py::RepoRegistry.unregister` | method |  |
| `indexer/repo_registry.py::RepoRegistry.get` | method |  |
| `indexer/repo_registry.py::RepoRegistry.list_names` | method |  |
| `indexer/repo_registry.py::RepoRegistry.items` | method |  |
| `indexer/repo_registry.py::RepoRegistry.update_meta` | method |  |
| `indexer/repository_benchmarks.py::run_repository_index_benchmark` | function |  |
| `indexer/repository_benchmarks.py::_sync_metrics` | function |  |
| `indexer/repository_benchmarks.py::_git` | function |  |
| `indexer/repository_benchmarks.py::_commit` | function |  |
| `indexer/repository_benchmarks.py::_percentile` | function |  |
| `indexer/repository_benchmarks.py::_database_bytes` | function |  |
| `indexer/repository_benchmarks.py::main` | function |  |
| `indexer/repository_embedding.py::ConfiguredEmbeddingProvider` | class | RepositoryIndex adapter for the configured OpenAI-compatible endpoint. |
| `indexer/repository_embedding.py::ConfiguredEmbeddingProvider.__init__` | method |  |
| `indexer/repository_embedding.py::ConfiguredEmbeddingProvider.embed_documents` | method |  |
| `indexer/repository_embedding.py::ConfiguredEmbeddingProvider.embed_query` | method |  |
| `indexer/repository_index.py::EmbeddingProvider` | class |  |
| `indexer/repository_index.py::EmbeddingProvider.embed_documents` | method |  |
| `indexer/repository_index.py::EmbeddingProvider.embed_query` | method |  |
| `indexer/repository_index.py::RepositoryIndexError` | class |  |
| `indexer/repository_index.py::RepositoryIndexError.__init__` | method |  |
| `indexer/repository_index.py::IndexScope` | class |  |
| `indexer/repository_index.py::SyncRequest` | class |  |
| `indexer/repository_index.py::SyncReport` | class |  |
| `indexer/repository_index.py::SearchRequest` | class |  |
| `indexer/repository_index.py::SearchHit` | class |  |
| `indexer/repository_index.py::SymbolRecord` | class |  |
| `indexer/repository_index.py::SearchResult` | class |  |
| `indexer/repository_index.py::IndexStatus` | class |  |
| `indexer/repository_index.py::EnrichmentReport` | class |  |
| `indexer/repository_index.py::IntegrityReport` | class |  |
| `indexer/repository_index.py::MaintenanceReport` | class |  |
| `indexer/repository_index.py::_Head` | class |  |
| `indexer/repository_index.py::_PreparedArtifacts` | class |  |
| `indexer/repository_index.py::_DenseState` | class |  |
| `indexer/repository_index.py::_MaintenanceCounts` | class |  |
| `indexer/repository_index.py::RepositoryIndex` | class | Transactional, content-addressed repository index.

Git capture, parsing, graph maintenance, FTS, enrichment, maintenance, and
transaction boundaries remain private implementation details behind a small
repository-oriented interface. |
| `indexer/repository_index.py::RepositoryIndex.__init__` | method |  |
| `indexer/repository_index.py::RepositoryIndex.open` | method |  |
| `indexer/repository_index.py::RepositoryIndex.sync` | method |  |
| `indexer/repository_index.py::RepositoryIndex.enrich` | method | Complete the pending dense revision for the current generation. |
| `indexer/repository_index.py::RepositoryIndex.search` | method |  |
| `indexer/repository_index.py::RepositoryIndex.inspect` | method |  |
| `indexer/repository_index.py::RepositoryIndex.integrity` | method | Check database pages and declared foreign-key relationships. |
| `indexer/repository_index.py::RepositoryIndex.maintain` | method | Recover interrupted enrichment and collect unreachable index state. |
| `indexer/repository_index.py::RepositoryIndex._maintain_state` | method |  |
| `indexer/repository_index.py::RepositoryIndex.symbols` | method | Return the current generation's structural symbol projection. |
| `indexer/repository_index.py::RepositoryIndex.files` | method | Return source paths visible from the current branch head. |
| `indexer/repository_index.py::RepositoryIndex.trace` | method | Traverse the current generation's resolved call graph breadth-first. |
| `indexer/repository_index.py::RepositoryIndex._symbol_records` | method |  |
| `indexer/repository_index.py::RepositoryIndex._prepare_artifacts` | method |  |
| `indexer/repository_index.py::RepositoryIndex._load_artifacts` | method |  |
| `indexer/repository_index.py::RepositoryIndex._load_embedding_vectors` | method |  |
| `indexer/repository_index.py::RepositoryIndex._mark_enrichment_failed` | method |  |
| `indexer/repository_index.py::RepositoryIndex._read_dense_state` | method |  |
| `indexer/repository_index.py::RepositoryIndex._dense_state` | method |  |
| `indexer/repository_index.py::RepositoryIndex._dense_unavailable` | method |  |
| `indexer/repository_index.py::RepositoryIndex._dense_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._publish_generation` | method |  |
| `indexer/repository_index.py::RepositoryIndex._delete_paths` | method |  |
| `indexer/repository_index.py::RepositoryIndex._delete_orphan_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._insert_entries` | method |  |
| `indexer/repository_index.py::RepositoryIndex._rebuild_relations` | method |  |
| `indexer/repository_index.py::RepositoryIndex._exact_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._lexical_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._fuse_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._related_candidates` | method |  |
| `indexer/repository_index.py::RepositoryIndex._read_head` | method |  |
| `indexer/repository_index.py::RepositoryIndex._head` | method |  |
| `indexer/repository_index.py::RepositoryIndex._validate_scope` | method |  |
| `indexer/repository_index.py::RepositoryIndex._raise_invalid` | method |  |
| `indexer/repository_index.py::_canonical_nodes` | function |  |
| `indexer/repository_index.py::_artifact_id` | function |  |
| `indexer/repository_index.py::_context_hash` | function |  |
| `indexer/repository_index.py::_fts_expression` | function |  |
| `indexer/repository_index.py::_search_hit` | function |  |
| `indexer/repository_index.py::_count` | function |  |
| `indexer/repository_index.py::_chunks` | function |  |
| `indexer/repository_index.py::_head_identity` | function |  |
| `indexer/repository_index.py::_key` | function |  |
| `indexer/repository_index.py::_provider_model` | function |  |
| `indexer/repository_index.py::_normalize_vector` | function |  |
| `indexer/repository_index.py::_pack_vector` | function |  |
| `indexer/repository_index.py::_unpack_vector` | function |  |
| `indexer/repository_index.py::_lsh_buckets` | function |  |
| `indexer/repository_index.py::_target` | function |  |
| `indexer/repository_index.py::_timestamp` | function |  |
| `indexer/repository_index.py::_elapsed_ms` | function |  |
| `indexer/repository_projection.py::ProjectionReport` | class |  |
| `indexer/repository_projection.py::write_repository_projection` | function | Render Wiki and Skill files from one already-published generation. |
| `indexer/repository_projection.py::_write_skill` | function |  |
| `indexer/repository_service.py::RepositoryService` | class | Application seam shared by CLI, REST, and MCP adapters. |
| `indexer/repository_service.py::RepositoryService.__init__` | method |  |
| `indexer/repository_service.py::RepositoryService.sync` | method |  |
| `indexer/repository_service.py::RepositoryService.search` | method |  |
| `indexer/repository_service.py::RepositoryService.lookup` | method |  |
| `indexer/repository_service.py::RepositoryService.trace` | method |  |
| `indexer/repository_service.py::RepositoryService.project` | method |  |
| `indexer/repository_service.py::RepositoryService.inspect` | method |  |
| `indexer/repository_service.py::resolve_revision` | function |  |
| `indexer/repository_service.py::default_branch` | function |  |
| `indexer/repository_service.py::_hit_dict` | function |  |
| `indexer/repository_service.py::_record_dict` | function |  |
| `indexer/repository_store.py::RepositoryStoreError` | class |  |
| `indexer/repository_store.py::RepositoryStore` | class | SQLite connection and schema lifecycle for RepositoryIndex. |
| `indexer/repository_store.py::RepositoryStore.__init__` | method |  |
| `indexer/repository_store.py::RepositoryStore.connect` | method |  |
| `indexer/repository_store.py::RepositoryStore.transaction` | method |  |
| `indexer/repository_store.py::RepositoryStore._initialize` | method |  |
| `indexer/rest_api.py::register_repo` | function |  |
| `indexer/rest_api.py::task_status` | function |  |
| `indexer/rest_api.py::validate_repo` | function |  |
| `indexer/rest_api.py::sync_repo` | function |  |
| `indexer/rest_api.py::_run_all_branches` | function |  |
| `indexer/rest_api.py::sync_all_branches` | function |  |
| `indexer/rest_api.py::update_repo_and_sync` | function | Atomically update repo metadata, discover branches, and synchronize them. |
| `indexer/rest_api.py::_run_sync_task_inner` | function |  |
| `indexer/rest_api.py::_run_sync_task` | function |  |
| `indexer/rest_api.py::_run_register_task` | function |  |
| `indexer/rest_api.py::_run_register_task_inner` | function |  |
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
| `indexer/rest_api.py::_LoggingMiddleware` | class |  |
| `indexer/rest_api.py::_LoggingMiddleware.dispatch` | method |  |
| `indexer/rest_api.py::_AuthMiddleware` | class |  |
| `indexer/rest_api.py::_AuthMiddleware.dispatch` | method |  |
| `indexer/rest_api.py::_invalid_body_handler` | function |  |
| `indexer/rest_api.py::_index_page` | function |  |
| `indexer/rest_api.py::_resolve_repos` | function |  |
| `indexer/rest_api.py::_InvalidBodyError` | class |  |
| `indexer/rest_api.py::_validate_diff_payload` | function |  |
| `indexer/rest_api.py::_parse_body` | function |  |
| `indexer/retrieval.py::truncate_documents` | function |  |
| `indexer/retrieval.py::search_symbols` | function |  |
| `indexer/retrieval.py::search_code` | function |  |
| `indexer/retrieval.py::get_by_ids` | function | Read structural records from the current generation. |
| `indexer/retrieval.py::resolve_symbol` | function |  |
| `indexer/retrieval.py::impact_analysis` | function |  |
| `indexer/retrieval.py::change_plan` | function |  |
| `indexer/retrieval.py::diagnose_index` | function |  |
| `indexer/retrieval.py::agent_protocol_bundle` | function |  |
| `indexer/retrieval.py::list_entry_points` | function |  |
| `indexer/retrieval.py::locate_from_error` | function |  |
| `indexer/retrieval.py::post_edit_verify` | function |  |
| `indexer/retrieval.py::stable_symbol_id` | function |  |
| `indexer/retrieval.py::change_set` | function |  |
| `indexer/retrieval.py::coverage_map` | function |  |
| `indexer/retrieval.py::index_diff_report` | function |  |
| `indexer/retrieval.py::cross_repo_graph` | function |  |
| `indexer/retrieval.py::agent_capabilities_manifest` | function |  |
| `indexer/retrieval.py::trace_call` | function |  |
| `indexer/retrieval.py::get_source_context` | function |  |
| `indexer/retrieval.py::get_index_status` | function |  |
| `indexer/retrieval.py::find_tests_for_symbol` | function |  |
| `indexer/retrieval.py::get_edit_context` | function |  |
| `indexer/retrieval.py::pre_edit_check` | function |  |
| `indexer/retrieval.py::recommend_test_commands` | function |  |
| `indexer/retrieval.py::_git_dirty_files` | function |  |
| `indexer/retrieval.py::_expand_with_call_graph` | function |  |
| `indexer/retrieval.py::_natural_language_alias_score` | function |  |
| `indexer/retrieval.py::_looks_like_entry_point` | function |  |
| `indexer/retrieval.py::_freshness_risks` | function |  |
| `indexer/retrieval.py::_infer_entry_point_kind_from_hit` | function |  |
| `indexer/retrieval.py::_extract_error_frames` | function |  |
| `indexer/retrieval.py::_extract_http_paths` | function |  |
| `indexer/retrieval.py::_extract_error_terms` | function |  |
| `indexer/retrieval.py::_git_diff` | function |  |
| `indexer/retrieval.py::_parse_diff_changed_files` | function |  |
| `indexer/retrieval.py::_parse_diff_new_ranges` | function |  |
| `indexer/retrieval.py::_symbols_for_changed_files` | function |  |
| `indexer/retrieval.py::_has_config_changes` | function |  |
| `indexer/retrieval.py::_has_code_changes` | function |  |
| `indexer/retrieval.py::_limit_list` | function |  |
| `indexer/retrieval.py::_normalize_source_signature` | function |  |
| `indexer/retrieval.py::_is_test_path` | function |  |
| `indexer/retrieval.py::_node_edges` | function |  |
| `indexer/retrieval.py::_stable_id_moves` | function |  |
| `indexer/retrieval.py::_extract_graphql_operations` | function |  |
| `indexer/retrieval.py::_looks_like_client_symbol` | function |  |
| `indexer/retrieval.py::_repo_nodes_for_graph` | function |  |
| `indexer/retrieval.py::_parse_json_list` | function |  |
| `indexer/ruby_parser.py::_get_ruby_language` | function |  |
| `indexer/ruby_parser.py::_extract_ruby_doc` | function |  |
| `indexer/ruby_parser.py::_extract_imports` | function |  |
| `indexer/ruby_parser.py::visit` | function |  |
| `indexer/ruby_parser.py::_extract_calls` | function |  |
| `indexer/ruby_parser.py::parse_ruby_file` | function |  |
| `indexer/rust_parser.py::_get_rust_language` | function |  |
| `indexer/rust_parser.py::_extract_rust_doc` | function |  |
| `indexer/rust_parser.py::_extract_imports` | function |  |
| `indexer/rust_parser.py::visit` | function |  |
| `indexer/rust_parser.py::_extract_calls` | function |  |
| `indexer/rust_parser.py::parse_rust_file` | function |  |
| `indexer/search_eval.py::SearchCase` | class |  |
| `indexer/search_eval.py::evaluate_search` | function |  |
| `indexer/task_store.py::TaskStore` | class |  |
| `indexer/task_store.py::TaskStore.__init__` | method |  |
| `indexer/task_store.py::TaskStore._cleanup` | method |  |
| `indexer/task_store.py::TaskStore.create` | method |  |
| `indexer/task_store.py::TaskStore.get` | method |  |
| `indexer/task_store.py::TaskStore.update` | method |  |
| `indexer/utils.py::resolve_api_key` | function |  |
| `indexer/utils.py::_rel` | function |  |
| `indexer/utils.py::_node_text` | function |  |
| `indexer/utils.py::_node_name` | function |  |
| `indexer/utils.py::load_env_file` | function |  |
| `indexer/wiki.py::PageContext` | class |  |
| `indexer/wiki.py::IndexEntry` | class |  |
| `indexer/wiki.py::_jinja_env` | function |  |
| `indexer/wiki.py::build_page` | function |  |
| `indexer/wiki.py::build_index` | function |  |
| `indexer/wiki.py::sanitize_group_label` | function |  |
| `indexer/wiki.py::resolve_wiki_page_path` | function |  |
| `indexer/wiki.py::_atomic_write_text` | function |  |
| `indexer/wiki.py::write_page` | function |  |
| `indexer/wiki.py::write_index` | function |  |
## Relationships
- **Calls:** indexer/agent_context.py::change_plan, indexer/agent_context.py::impact_analysis, indexer/agent_context.py::list_entry_points, indexer/agent_context.py::locate_from_error, indexer/agent_context.py::resolve_symbol, indexer/agent_contracts.py::_agent_json_schema, indexer/agent_contracts.py::_capability_example, indexer/agent_contracts.py::_capability_input_schema, indexer/agent_contracts.py::_capability_next_tools, indexer/agent_contracts.py::_capability_required_output, indexer/agent_contracts.py::_endpoint_specs, indexer/agent_contracts.py::_field_schema, indexer/agent_contracts.py::_object_schema, indexer/agent_contracts.py::agent_capabilities_manifest, indexer/agent_diagnostics.py::diagnose_index, indexer/agent_diff.py::change_set, indexer/agent_diff.py::coverage_map, indexer/agent_diff.py::index_diff_report, indexer/agent_diff.py::post_edit_verify, indexer/agent_diff.py::stable_symbol_id, indexer/agent_graph.py::cross_repo_graph, indexer/ast_parser.py::ASTNode, indexer/ast_parser.py::_attach_source, indexer/ast_parser.py::_entry_point_from_decorators, indexer/ast_parser.py::_extract_calls, indexer/ast_parser.py::_extract_imports, indexer/ast_parser.py::_get_class_method_ids, indexer/ast_parser.py::parse_file, indexer/cli.py::_ensure_cache_gitignore, indexer/cli.py::_json_dumps, indexer/cli.py::agent_schema, indexer/cli.py::maintain, indexer/cli.py::run, indexer/config.py::Config, indexer/config.py::EmbeddingConfig, indexer/config.py::_apply_env, indexer/config.py::_apply_env_field, indexer/config.py::_env, indexer/config.py::_env_int, indexer/config.py::load_config, indexer/config.py::save_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_get_openai_client, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::embed_texts, indexer/git.py::_run, indexer/git.py::current_branch, indexer/git.py::is_git_repo, indexer/git_ops.py::GitOperationError, indexer/git_ops.py::GitOperationError.__init__, indexer/git_ops.py::_cleanup_worktree, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_err, indexer/git_ops.py::_inject_credentials, indexer/git_ops.py::_match_branch_rule, indexer/git_ops.py::_sanitize_error, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/git_ops.py::git_fetch_refs, indexer/git_snapshot.py::GitSnapshot, indexer/git_snapshot.py::GitSnapshot._capture_staged_tree, indexer/git_snapshot.py::GitSnapshot._capture_worktree_tree, indexer/git_snapshot.py::GitSnapshot._entries_for_paths, indexer/git_snapshot.py::GitSnapshot._list_tree, indexer/git_snapshot.py::GitSnapshot._object_environment, indexer/git_snapshot.py::GitSnapshot._remove_generated_paths, indexer/git_snapshot.py::GitSnapshot._run_bytes, indexer/git_snapshot.py::GitSnapshot._run_text, indexer/git_snapshot.py::GitSnapshot.close, indexer/git_snapshot.py::GitSnapshot.delta, indexer/git_snapshot.py::GitSnapshot.initial_delta, indexer/git_snapshot.py::GitSnapshot.prune_snapshots, indexer/git_snapshot.py::GitSnapshot.read_blobs, indexer/git_snapshot.py::GitSnapshot.resolve_tree, indexer/git_snapshot.py::GitSnapshotError, indexer/git_snapshot.py::TreeDelta, indexer/git_snapshot.py::TreeEntry, indexer/git_snapshot.py::_is_indexable, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_go_language, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::folder_of, indexer/grouper.py::prefixes, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_command, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/hooks.py::remove_hook, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::_get_java_language, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_export_type_star_span, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_get_language, indexer/js_parser.py::_import_type_expression, indexer/js_parser.py::_is_type_only_import, indexer/js_parser.py::_mask_span, indexer/js_parser.py::_normalize_typescript_tree, indexer/js_parser.py::_walk_tree, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/mcp_server.py::_MCPAuthMiddleware, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_api_request, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/repo_registry.py::RepoRegistry._save, indexer/repo_registry.py::RepoRegistry.get, indexer/repo_registry.py::RepoRegistry.items, indexer/repo_registry.py::RepoRegistry.list_names, indexer/repo_registry.py::RepoRegistry.register, indexer/repo_registry.py::RepoRegistry.unregister, indexer/repo_registry.py::RepoRegistry.update_meta, indexer/repo_registry.py::_get_repo_lock, indexer/repository_benchmarks.py::_commit, indexer/repository_benchmarks.py::_database_bytes, indexer/repository_benchmarks.py::_git, indexer/repository_benchmarks.py::_percentile, indexer/repository_benchmarks.py::_sync_metrics, indexer/repository_benchmarks.py::run_repository_index_benchmark, indexer/repository_embedding.py::ConfiguredEmbeddingProvider, indexer/repository_embedding.py::ConfiguredEmbeddingProvider.embed_query, indexer/repository_index.py::EmbeddingProvider.embed_documents, indexer/repository_index.py::EmbeddingProvider.embed_query, indexer/repository_index.py::EnrichmentReport, indexer/repository_index.py::IndexScope, indexer/repository_index.py::IndexStatus, indexer/repository_index.py::IntegrityReport, indexer/repository_index.py::MaintenanceReport, indexer/repository_index.py::RepositoryIndex, indexer/repository_index.py::RepositoryIndex.__init__, indexer/repository_index.py::RepositoryIndex._delete_orphan_candidates, indexer/repository_index.py::RepositoryIndex._delete_paths, indexer/repository_index.py::RepositoryIndex._dense_candidates, indexer/repository_index.py::RepositoryIndex._dense_state, indexer/repository_index.py::RepositoryIndex._dense_unavailable, indexer/repository_index.py::RepositoryIndex._exact_candidates, indexer/repository_index.py::RepositoryIndex._fuse_candidates, indexer/repository_index.py::RepositoryIndex._head, indexer/repository_index.py::RepositoryIndex._insert_entries, indexer/repository_index.py::RepositoryIndex._lexical_candidates, indexer/repository_index.py::RepositoryIndex._load_artifacts, indexer/repository_index.py::RepositoryIndex._load_embedding_vectors, indexer/repository_index.py::RepositoryIndex._maintain_state, indexer/repository_index.py::RepositoryIndex._mark_enrichment_failed, indexer/repository_index.py::RepositoryIndex._prepare_artifacts, indexer/repository_index.py::RepositoryIndex._publish_generation, indexer/repository_index.py::RepositoryIndex._raise_invalid, indexer/repository_index.py::RepositoryIndex._read_dense_state, indexer/repository_index.py::RepositoryIndex._read_head, indexer/repository_index.py::RepositoryIndex._rebuild_relations, indexer/repository_index.py::RepositoryIndex._related_candidates, indexer/repository_index.py::RepositoryIndex._symbol_records, indexer/repository_index.py::RepositoryIndex._validate_scope, indexer/repository_index.py::RepositoryIndex.enrich, indexer/repository_index.py::RepositoryIndex.files, indexer/repository_index.py::RepositoryIndex.inspect, indexer/repository_index.py::RepositoryIndex.integrity, indexer/repository_index.py::RepositoryIndex.open, indexer/repository_index.py::RepositoryIndex.search, indexer/repository_index.py::RepositoryIndex.symbols, indexer/repository_index.py::RepositoryIndex.sync, indexer/repository_index.py::RepositoryIndex.trace, indexer/repository_index.py::RepositoryIndexError, indexer/repository_index.py::RepositoryIndexError.__init__, indexer/repository_index.py::SearchHit, indexer/repository_index.py::SearchRequest, indexer/repository_index.py::SearchResult, indexer/repository_index.py::SymbolRecord, indexer/repository_index.py::SyncReport, indexer/repository_index.py::SyncRequest, indexer/repository_index.py::_DenseState, indexer/repository_index.py::_Head, indexer/repository_index.py::_MaintenanceCounts, indexer/repository_index.py::_PreparedArtifacts, indexer/repository_index.py::_artifact_id, indexer/repository_index.py::_canonical_nodes, indexer/repository_index.py::_chunks, indexer/repository_index.py::_context_hash, indexer/repository_index.py::_count, indexer/repository_index.py::_elapsed_ms, indexer/repository_index.py::_fts_expression, indexer/repository_index.py::_head_identity, indexer/repository_index.py::_key, indexer/repository_index.py::_lsh_buckets, indexer/repository_index.py::_normalize_vector, indexer/repository_index.py::_pack_vector, indexer/repository_index.py::_provider_model, indexer/repository_index.py::_search_hit, indexer/repository_index.py::_target, indexer/repository_index.py::_timestamp, indexer/repository_index.py::_unpack_vector, indexer/repository_projection.py::ProjectionReport, indexer/repository_projection.py::_write_skill, indexer/repository_projection.py::write_repository_projection, indexer/repository_service.py::RepositoryService, indexer/repository_service.py::RepositoryService.inspect, indexer/repository_service.py::RepositoryService.lookup, indexer/repository_service.py::RepositoryService.project, indexer/repository_service.py::RepositoryService.search, indexer/repository_service.py::RepositoryService.sync, indexer/repository_service.py::RepositoryService.trace, indexer/repository_service.py::_hit_dict, indexer/repository_service.py::_record_dict, indexer/repository_service.py::default_branch, indexer/repository_service.py::resolve_revision, indexer/repository_store.py::RepositoryStore, indexer/repository_store.py::RepositoryStore._initialize, indexer/repository_store.py::RepositoryStore.connect, indexer/repository_store.py::RepositoryStore.transaction, indexer/repository_store.py::RepositoryStoreError, indexer/rest_api.py::_InvalidBodyError, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_resolve_repos, indexer/rest_api.py::_run_all_branches, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task_inner, indexer/rest_api.py::_validate_diff_payload, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::_webhook_sign, indexer/rest_api.py::change_plan, indexer/rest_api.py::change_set, indexer/rest_api.py::coverage_map, indexer/rest_api.py::create_app, indexer/rest_api.py::cross_repo_graph, indexer/rest_api.py::diagnose_index, indexer/rest_api.py::find_tests_for_symbol, indexer/rest_api.py::get_edit_context, indexer/rest_api.py::get_source_context, indexer/rest_api.py::impact_analysis, indexer/rest_api.py::index_diff_report, indexer/rest_api.py::list_entry_points, indexer/rest_api.py::locate_from_error, indexer/rest_api.py::post_edit_verify, indexer/rest_api.py::pre_edit_check, indexer/rest_api.py::resolve_symbol, indexer/rest_api.py::search_symbols, indexer/rest_api.py::trace_call, indexer/retrieval.py::_extract_error_frames, indexer/retrieval.py::_extract_error_terms, indexer/retrieval.py::_extract_graphql_operations, indexer/retrieval.py::_extract_http_paths, indexer/retrieval.py::_freshness_risks, indexer/retrieval.py::_git_diff, indexer/retrieval.py::_git_dirty_files, indexer/retrieval.py::_has_code_changes, indexer/retrieval.py::_has_config_changes, indexer/retrieval.py::_infer_entry_point_kind_from_hit, indexer/retrieval.py::_is_test_path, indexer/retrieval.py::_limit_list, indexer/retrieval.py::_looks_like_client_symbol, indexer/retrieval.py::_looks_like_entry_point, indexer/retrieval.py::_natural_language_alias_score, indexer/retrieval.py::_node_edges, indexer/retrieval.py::_normalize_source_signature, indexer/retrieval.py::_parse_diff_changed_files, indexer/retrieval.py::_parse_diff_new_ranges, indexer/retrieval.py::_parse_json_list, indexer/retrieval.py::_repo_nodes_for_graph, indexer/retrieval.py::_stable_id_moves, indexer/retrieval.py::_symbols_for_changed_files, indexer/retrieval.py::agent_capabilities_manifest, indexer/retrieval.py::agent_protocol_bundle, indexer/retrieval.py::change_plan, indexer/retrieval.py::change_set, indexer/retrieval.py::coverage_map, indexer/retrieval.py::cross_repo_graph, indexer/retrieval.py::diagnose_index, indexer/retrieval.py::find_tests_for_symbol, indexer/retrieval.py::get_by_ids, indexer/retrieval.py::get_edit_context, indexer/retrieval.py::get_index_status, indexer/retrieval.py::get_source_context, indexer/retrieval.py::impact_analysis, indexer/retrieval.py::index_diff_report, indexer/retrieval.py::list_entry_points, indexer/retrieval.py::locate_from_error, indexer/retrieval.py::post_edit_verify, indexer/retrieval.py::pre_edit_check, indexer/retrieval.py::recommend_test_commands, indexer/retrieval.py::resolve_symbol, indexer/retrieval.py::search_code, indexer/retrieval.py::search_symbols, indexer/retrieval.py::stable_symbol_id, indexer/retrieval.py::trace_call, indexer/retrieval.py::truncate_documents, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::_get_ruby_language, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::_get_rust_language, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/task_store.py::TaskStore._cleanup, indexer/task_store.py::TaskStore.create, indexer/task_store.py::TaskStore.get, indexer/task_store.py::TaskStore.update, indexer/utils.py::_node_text, indexer/utils.py::_rel, indexer/utils.py::load_env_file, indexer/utils.py::resolve_api_key, indexer/wiki.py::IndexEntry, indexer/wiki.py::PageContext, indexer/wiki.py::_atomic_write_text, indexer/wiki.py::_jinja_env, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::sanitize_group_label, indexer/wiki.py::write_index, indexer/wiki.py::write_page, tests/fixtures/sample_ruby/app.rb::Parser, tests/fixtures/sample_ruby/app.rb::Parser.parse, tests/fixtures/sample_rust/lib.rs::User.new
- **Called by:** indexer/agent_context.py::change_plan, indexer/agent_context.py::impact_analysis, indexer/agent_context.py::list_entry_points, indexer/agent_context.py::locate_from_error, indexer/agent_context.py::resolve_symbol, indexer/agent_contracts.py::_agent_json_schema, indexer/agent_contracts.py::_capability_example, indexer/agent_contracts.py::_capability_input_schema, indexer/agent_contracts.py::_capability_next_tools, indexer/agent_contracts.py::_capability_required_output, indexer/agent_contracts.py::_endpoint_specs, indexer/agent_contracts.py::_field_schema, indexer/agent_contracts.py::_object_schema, indexer/agent_contracts.py::agent_capabilities_manifest, indexer/agent_contracts.py::agent_schema, indexer/agent_diagnostics.py::diagnose_index, indexer/agent_diff.py::change_set, indexer/agent_diff.py::coverage_map, indexer/agent_diff.py::index_diff_report, indexer/agent_diff.py::post_edit_verify, indexer/agent_diff.py::stable_symbol_id, indexer/agent_graph.py::cross_repo_graph, indexer/ast_parser.py::parse_file, indexer/cli.py::agent_capabilities, indexer/cli.py::agent_context, indexer/cli.py::agent_diagnose, indexer/cli.py::agent_plan, indexer/cli.py::agent_schema, indexer/cli.py::agent_verify, indexer/cli.py::hook_install, indexer/cli.py::hook_remove, indexer/cli.py::init, indexer/cli.py::maintain, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/config.py::_apply_env, indexer/config.py::_env, indexer/config.py::_env_int, indexer/config.py::load_config, indexer/embedding.py::_call_embedding_api, indexer/embedding.py::_resolve_api_key, indexer/embedding.py::embed_query, indexer/embedding.py::embed_texts, indexer/git.py::_run, indexer/git.py::current_branch, indexer/git.py::is_git_repo, indexer/git_ops.py::GitOperationError.__init__, indexer/git_ops.py::_cleanup_worktree, indexer/git_ops.py::_detect_default_branch, indexer/git_ops.py::_discover_remote_branches, indexer/git_ops.py::_err, indexer/git_ops.py::_store_credentials, indexer/git_ops.py::git_fetch_checkout_pull, indexer/git_ops.py::git_fetch_refs, indexer/git_snapshot.py::GitSnapshot.__exit__, indexer/git_snapshot.py::GitSnapshot._capture_staged_tree, indexer/git_snapshot.py::GitSnapshot._capture_worktree_tree, indexer/git_snapshot.py::GitSnapshot._entries_for_paths, indexer/git_snapshot.py::GitSnapshot._list_tree, indexer/git_snapshot.py::GitSnapshot._object_environment, indexer/git_snapshot.py::GitSnapshot._remove_generated_paths, indexer/git_snapshot.py::GitSnapshot._run_bytes, indexer/git_snapshot.py::GitSnapshot._run_text, indexer/git_snapshot.py::GitSnapshot.delta, indexer/git_snapshot.py::GitSnapshot.initial_delta, indexer/git_snapshot.py::GitSnapshot.prune_snapshots, indexer/git_snapshot.py::GitSnapshot.read_blobs, indexer/git_snapshot.py::GitSnapshot.resolve_tree, indexer/go_parser.py::_extract_calls, indexer/go_parser.py::_extract_go_doc, indexer/go_parser.py::_extract_imports, indexer/go_parser.py::_get_receiver, indexer/go_parser.py::parse_go_file, indexer/go_parser.py::visit, indexer/grouper.py::density_group, indexer/grouper.py::resolve_group, indexer/hooks.py::_hook_script_append, indexer/hooks.py::_hook_script_fresh, indexer/hooks.py::install_hook, indexer/java_parser.py::_extract_calls, indexer/java_parser.py::_extract_imports, indexer/java_parser.py::_extract_javadoc, indexer/java_parser.py::parse_java_file, indexer/java_parser.py::visit, indexer/js_parser.py::_extract_calls, indexer/js_parser.py::_extract_imports, indexer/js_parser.py::_extract_jsdoc, indexer/js_parser.py::_is_type_only_import, indexer/js_parser.py::_normalize_typescript_tree, indexer/js_parser.py::parse_js_file, indexer/js_parser.py::visit, indexer/mcp_server.py::_MCPAuthMiddleware.dispatch, indexer/mcp_server.py::_api_get, indexer/mcp_server.py::_api_post, indexer/mcp_server.py::_apply_mcp_auth, indexer/mcp_server.py::_patched_method, indexer/mcp_server.py::agent_capabilities_manifest_tool, indexer/mcp_server.py::agent_protocol_tool, indexer/mcp_server.py::change_plan_tool, indexer/mcp_server.py::change_set_tool, indexer/mcp_server.py::coverage_map_tool, indexer/mcp_server.py::create_api_server, indexer/mcp_server.py::create_server, indexer/mcp_server.py::cross_repo_graph_tool, indexer/mcp_server.py::diagnose_index_tool, indexer/mcp_server.py::find_tests_for_symbol_tool, indexer/mcp_server.py::get_edit_context_tool, indexer/mcp_server.py::get_index_status_tool, indexer/mcp_server.py::get_source_context_tool, indexer/mcp_server.py::impact_analysis_tool, indexer/mcp_server.py::index_diff_report_tool, indexer/mcp_server.py::list_entry_points_tool, indexer/mcp_server.py::list_repos, indexer/mcp_server.py::locate_from_error_tool, indexer/mcp_server.py::post_edit_verify_tool, indexer/mcp_server.py::pre_edit_check_tool, indexer/mcp_server.py::resolve_symbol_tool, indexer/mcp_server.py::search_symbols_tool, indexer/mcp_server.py::stable_symbol_id_tool, indexer/mcp_server.py::trace_call_tool, indexer/repo_registry.py::RepoRegistry._load, indexer/repo_registry.py::RepoRegistry._save, indexer/repo_registry.py::RepoRegistry.get, indexer/repo_registry.py::RepoRegistry.items, indexer/repo_registry.py::RepoRegistry.register, indexer/repo_registry.py::RepoRegistry.unregister, indexer/repo_registry.py::RepoRegistry.update_meta, indexer/repo_registry.py::_get_repo_lock, indexer/repository_benchmarks.py::_commit, indexer/repository_benchmarks.py::_git, indexer/repository_benchmarks.py::main, indexer/repository_benchmarks.py::run_repository_index_benchmark, indexer/repository_embedding.py::ConfiguredEmbeddingProvider.embed_documents, indexer/repository_embedding.py::ConfiguredEmbeddingProvider.embed_query, indexer/repository_index.py::RepositoryIndex.__init__, indexer/repository_index.py::RepositoryIndex._delete_orphan_candidates, indexer/repository_index.py::RepositoryIndex._delete_paths, indexer/repository_index.py::RepositoryIndex._dense_candidates, indexer/repository_index.py::RepositoryIndex._dense_state, indexer/repository_index.py::RepositoryIndex._dense_unavailable, indexer/repository_index.py::RepositoryIndex._exact_candidates, indexer/repository_index.py::RepositoryIndex._fuse_candidates, indexer/repository_index.py::RepositoryIndex._head, indexer/repository_index.py::RepositoryIndex._insert_entries, indexer/repository_index.py::RepositoryIndex._lexical_candidates, indexer/repository_index.py::RepositoryIndex._load_artifacts, indexer/repository_index.py::RepositoryIndex._load_embedding_vectors, indexer/repository_index.py::RepositoryIndex._maintain_state, indexer/repository_index.py::RepositoryIndex._mark_enrichment_failed, indexer/repository_index.py::RepositoryIndex._prepare_artifacts, indexer/repository_index.py::RepositoryIndex._publish_generation, indexer/repository_index.py::RepositoryIndex._raise_invalid, indexer/repository_index.py::RepositoryIndex._read_dense_state, indexer/repository_index.py::RepositoryIndex._read_head, indexer/repository_index.py::RepositoryIndex._rebuild_relations, indexer/repository_index.py::RepositoryIndex._related_candidates, indexer/repository_index.py::RepositoryIndex._symbol_records, indexer/repository_index.py::RepositoryIndex._validate_scope, indexer/repository_index.py::RepositoryIndex.enrich, indexer/repository_index.py::RepositoryIndex.files, indexer/repository_index.py::RepositoryIndex.inspect, indexer/repository_index.py::RepositoryIndex.integrity, indexer/repository_index.py::RepositoryIndex.maintain, indexer/repository_index.py::RepositoryIndex.search, indexer/repository_index.py::RepositoryIndex.symbols, indexer/repository_index.py::RepositoryIndex.sync, indexer/repository_index.py::RepositoryIndex.trace, indexer/repository_index.py::RepositoryIndexError.__init__, indexer/repository_index.py::_provider_model, indexer/repository_index.py::_search_hit, indexer/repository_projection.py::_write_skill, indexer/repository_projection.py::write_repository_projection, indexer/repository_service.py::RepositoryService.__init__, indexer/repository_service.py::RepositoryService.inspect, indexer/repository_service.py::RepositoryService.lookup, indexer/repository_service.py::RepositoryService.project, indexer/repository_service.py::RepositoryService.search, indexer/repository_service.py::RepositoryService.sync, indexer/repository_service.py::RepositoryService.trace, indexer/repository_service.py::_hit_dict, indexer/repository_service.py::default_branch, indexer/repository_service.py::resolve_revision, indexer/repository_store.py::RepositoryStore.__init__, indexer/repository_store.py::RepositoryStore._initialize, indexer/repository_store.py::RepositoryStore.connect, indexer/repository_store.py::RepositoryStore.transaction, indexer/rest_api.py::_AuthMiddleware.dispatch, indexer/rest_api.py::_get_webhook_url, indexer/rest_api.py::_parse_body, indexer/rest_api.py::_resolve_repos, indexer/rest_api.py::_run_all_branches, indexer/rest_api.py::_run_register_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_run_sync_task_inner, indexer/rest_api.py::_verify_webhook_sign, indexer/rest_api.py::_webhook_sign, indexer/rest_api.py::agent_protocol, indexer/rest_api.py::change_plan, indexer/rest_api.py::change_set, indexer/rest_api.py::coverage_map, indexer/rest_api.py::create_app, indexer/rest_api.py::cross_repo_graph, indexer/rest_api.py::diagnose_index, indexer/rest_api.py::find_tests_for_symbol, indexer/rest_api.py::get_edit_context, indexer/rest_api.py::get_source_context, indexer/rest_api.py::health, indexer/rest_api.py::impact_analysis, indexer/rest_api.py::index_diff_report, indexer/rest_api.py::index_status, indexer/rest_api.py::list_entry_points, indexer/rest_api.py::list_repos, indexer/rest_api.py::locate_from_error, indexer/rest_api.py::multi_repo_skill, indexer/rest_api.py::post_edit_verify, indexer/rest_api.py::pre_edit_check, indexer/rest_api.py::register_repo, indexer/rest_api.py::repo_detail, indexer/rest_api.py::resolve_symbol, indexer/rest_api.py::search_symbols, indexer/rest_api.py::stable_symbol_id_endpoint, indexer/rest_api.py::sync_all_branches, indexer/rest_api.py::sync_repo, indexer/rest_api.py::task_status, indexer/rest_api.py::trace_call, indexer/rest_api.py::unregister_repo, indexer/rest_api.py::update_repo_and_sync, indexer/rest_api.py::update_repo_meta, indexer/rest_api.py::validate_repo, indexer/rest_api.py::webhook_by_name, indexer/rest_api.py::wiki_page_content, indexer/retrieval.py::_expand_with_call_graph, indexer/retrieval.py::_freshness_risks, indexer/retrieval.py::_git_diff, indexer/retrieval.py::_git_dirty_files, indexer/retrieval.py::_infer_entry_point_kind_from_hit, indexer/retrieval.py::_looks_like_client_symbol, indexer/retrieval.py::_looks_like_entry_point, indexer/retrieval.py::_natural_language_alias_score, indexer/retrieval.py::_node_edges, indexer/retrieval.py::_parse_diff_new_ranges, indexer/retrieval.py::_repo_nodes_for_graph, indexer/retrieval.py::_stable_id_moves, indexer/retrieval.py::_symbols_for_changed_files, indexer/retrieval.py::agent_protocol_bundle, indexer/retrieval.py::find_tests_for_symbol, indexer/retrieval.py::get_by_ids, indexer/retrieval.py::get_edit_context, indexer/retrieval.py::get_index_status, indexer/retrieval.py::pre_edit_check, indexer/retrieval.py::recommend_test_commands, indexer/retrieval.py::search_code, indexer/retrieval.py::search_symbols, indexer/retrieval.py::trace_call, indexer/ruby_parser.py::_extract_calls, indexer/ruby_parser.py::_extract_imports, indexer/ruby_parser.py::_extract_ruby_doc, indexer/ruby_parser.py::parse_ruby_file, indexer/ruby_parser.py::visit, indexer/rust_parser.py::_extract_calls, indexer/rust_parser.py::_extract_imports, indexer/rust_parser.py::_extract_rust_doc, indexer/rust_parser.py::parse_rust_file, indexer/rust_parser.py::visit, indexer/search_eval.py::evaluate_search, indexer/task_store.py::TaskStore._cleanup, indexer/task_store.py::TaskStore.create, indexer/task_store.py::TaskStore.get, indexer/task_store.py::TaskStore.update, indexer/utils.py::_node_name, indexer/utils.py::resolve_api_key, indexer/wiki.py::build_index, indexer/wiki.py::build_page, indexer/wiki.py::resolve_wiki_page_path, indexer/wiki.py::write_index, indexer/wiki.py::write_page, tests/test_api_contracts.py::test_agent_capabilities_all_tools_have_schemas, tests/test_api_contracts.py::test_agent_capabilities_endpoint_contract, tests/test_api_contracts.py::test_agent_schema_endpoint_exports_machine_readable_contract, tests/test_api_contracts.py::test_core_tool_contract_top_level_keys, tests/test_api_contracts.py::test_post_edit_verify_endpoint_rejects_oversized_diff, tests/test_api_contracts.py::test_stable_symbol_id_endpoint_contract, tests/test_ast_parser.py::test_calls_extracted, tests/test_ast_parser.py::test_class_node, tests/test_ast_parser.py::test_docstring_extracted, tests/test_ast_parser.py::test_function_node, tests/test_ast_parser.py::test_imports_extracted, tests/test_ast_parser.py::test_java_class_node, tests/test_ast_parser.py::test_java_enum_node, tests/test_ast_parser.py::test_java_imports_extracted, tests/test_ast_parser.py::test_java_interface_node, tests/test_ast_parser.py::test_java_javadoc_extracted, tests/test_ast_parser.py::test_java_method_node, tests/test_ast_parser.py::test_java_parse_returns_nodes, tests/test_ast_parser.py::test_method_node, tests/test_ast_parser.py::test_parse_returns_nodes, tests/test_ast_parser.py::test_python_click_command_entry_point, tests/test_ast_parser.py::test_python_fastapi_route_entry_point, tests/test_ast_parser.py::test_ruby_class_node, tests/test_ast_parser.py::test_ruby_docstring_extracted, tests/test_ast_parser.py::test_ruby_function_node, tests/test_ast_parser.py::test_ruby_method_node, tests/test_ast_parser.py::test_ruby_module_node, tests/test_ast_parser.py::test_ruby_parse_returns_nodes, tests/test_ast_parser.py::test_rust_docstring_extracted, tests/test_ast_parser.py::test_rust_enum_node, tests/test_ast_parser.py::test_rust_function_node, tests/test_ast_parser.py::test_rust_imports_extracted, tests/test_ast_parser.py::test_rust_method_node, tests/test_ast_parser.py::test_rust_parse_returns_nodes, tests/test_ast_parser.py::test_rust_struct_node, tests/test_ast_parser.py::test_rust_trait_method_spec, tests/test_ast_parser.py::test_rust_trait_node, tests/test_ast_parser.py::test_rust_type_alias, tests/test_ast_parser.py::test_typescript_import_type_array_in_generic_preserves_structure, tests/test_ast_parser.py::test_typescript_import_types_in_generic_calls_preserve_structure, tests/test_ast_parser.py::test_typescript_runtime_dynamic_import_is_not_normalized, tests/test_config.py::_restore_env, tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_grouper.py::test_deep_sparse_merges_upward, tests/test_grouper.py::test_dense_folder_gets_own_page, tests/test_grouper.py::test_different_folders_get_separate_groups, tests/test_grouper.py::test_returns_all_files, tests/test_grouper.py::test_root_files_count_correctly, tests/test_grouper.py::test_root_level_files, tests/test_grouper.py::test_sparse_folders_merge_to_parent, tests/test_performance_baseline.py::test_repository_index_generation_cost_scales_with_delta, tests/test_repository_adapters.py::_git, tests/test_repository_adapters.py::test_agent_context_and_diagnostics_read_repository_generation, tests/test_repository_adapters.py::test_branch_status_isolated_in_same_database, tests/test_repository_adapters.py::test_remote_tracking_ref_wins_over_stale_local_branch, tests/test_repository_adapters.py::test_rest_local_repo_uses_current_branch_when_registry_has_no_branch, tests/test_repository_adapters.py::test_rest_search_requires_explicit_branch_and_preserves_scope, tests/test_repository_adapters.py::test_rest_trace_rejects_unknown_branch, tests/test_repository_adapters.py::test_retrieval_and_service_return_the_same_generation_and_order, tests/test_repository_index.py::_git, tests/test_repository_index.py::_index, tests/test_repository_index.py::test_blob_artifact_survives_rename_without_stale_component_ids, tests/test_repository_index.py::test_branch_scope_is_explicit_and_results_do_not_leak, tests/test_repository_index.py::test_cross_branch_enrichment_reuses_content_addressed_vectors, tests/test_repository_index.py::test_dense_query_failure_degrades_preferred_and_fails_required, tests/test_repository_index.py::test_enrichment_is_idempotent_for_published_model_and_generation, tests/test_repository_index.py::test_enrichment_revision_is_atomic_and_enables_dense_recall, tests/test_repository_index.py::test_failed_enrichment_keeps_structural_generation_searchable, tests/test_repository_index.py::test_incremental_enrichment_embeds_only_changed_content, tests/test_repository_index.py::test_incremental_sync_updates_and_removes_only_changed_paths, tests/test_repository_index.py::test_integrity_reports_foreign_key_violations, tests/test_repository_index.py::test_maintenance_recovers_interrupted_current_enrichment, tests/test_repository_index.py::test_modern_typescript_type_only_syntax_publishes, tests/test_repository_index.py::test_non_source_tree_change_publishes_snapshot_without_parsing, tests/test_repository_index.py::test_parse_failure_does_not_advance_visible_generation, tests/test_repository_index.py::test_repository_index_quality_gate_uses_real_git_corpus, tests/test_repository_index.py::test_same_blob_is_parsed_once_across_branches, tests/test_repository_index.py::test_search_combines_exact_and_fts_and_separates_related_symbols, tests/test_repository_index.py::test_staged_revision_captures_index_without_changing_git_state, tests/test_repository_index.py::test_symbols_project_current_generation_with_resolved_relations, tests/test_repository_index.py::test_sync_collects_old_generations_and_orphan_artifacts, tests/test_repository_index.py::test_sync_publishes_generation_and_inspect_reports_same_snapshot, tests/test_repository_index.py::test_trace_reads_current_generation_call_graph_in_both_directions, tests/test_repository_index.py::test_transaction_failure_rolls_back_materialized_state, tests/test_repository_index.py::test_tree_sitter_syntax_error_is_rejected, tests/test_repository_index.py::test_typescript_import_type_array_in_generic_publishes, tests/test_repository_index.py::test_typescript_import_type_repair_does_not_hide_other_errors, tests/test_repository_index.py::test_unchanged_tree_is_constant_work_and_does_not_parse, tests/test_repository_index.py::test_valid_source_without_symbols_is_not_treated_as_parse_failure, tests/test_repository_index.py::test_wiki_projection_is_rendered_from_published_generation, tests/test_repository_index.py::test_worktree_revision_captures_unstaged_and_untracked_without_staging, tests/test_runtime_safety.py::test_pre_commit_hook_uses_atomic_local_generation_command, tests/test_runtime_safety.py::test_register_rejects_invalid_url_before_background_work, tests/test_runtime_safety.py::test_registry_update_and_unregister_are_self_contained, tests/test_runtime_safety.py::test_source_context_rejects_path_escape, tests/test_runtime_safety.py::test_task_store_returns_copies_and_keeps_running_tasks_during_cleanup, tests/test_wiki.py::_make_node, tests/test_wiki.py::test_build_index_contains_page, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** __future__.annotations, array.array, ast, asyncio, click, collections.abc.Sequence, collections.defaultdict, concurrent.futures.ThreadPoolExecutor, concurrent.futures.as_completed, contextlib.contextmanager, copy, dataclasses.asdict, dataclasses.dataclass, dataclasses.field, datetime.UTC, datetime.datetime, fnmatch, hashlib, hmac, indexer.agent_context.change_plan, indexer.agent_context.get_edit_context, indexer.agent_context.impact_analysis, indexer.agent_context.list_entry_points, indexer.agent_context.locate_from_error, indexer.agent_context.resolve_symbol, indexer.agent_contracts.agent_capabilities_manifest, indexer.agent_contracts.agent_schema, indexer.agent_diagnostics.diagnose_index, indexer.agent_diff.change_set, indexer.agent_diff.coverage_map, indexer.agent_diff.index_diff_report, indexer.agent_diff.post_edit_verify, indexer.agent_diff.stable_symbol_id, indexer.agent_graph.cross_repo_graph, indexer.agent_protocol.agent_capabilities_manifest, indexer.agent_protocol.agent_schema, indexer.ast_parser.ASTNode, indexer.ast_parser.parse_file, indexer.cli._ensure_cache_gitignore, indexer.config.Config, indexer.config.EmbeddingConfig, indexer.config.load_config, indexer.config.save_config, indexer.embedding.embed_query, indexer.embedding.embed_texts, indexer.git._GIT_ENV, indexer.git.current_branch, indexer.git.is_git_repo, indexer.git_ops.GitOperationError, indexer.git_ops._detect_default_branch, indexer.git_ops._discover_remote_branches, indexer.git_ops._inject_credentials, indexer.git_ops._match_branch_rule, indexer.git_ops._sanitize_error, indexer.git_ops._store_credentials, indexer.git_ops.git_fetch_checkout_pull, indexer.git_ops.git_fetch_refs, indexer.git_snapshot.GitSnapshot, indexer.git_snapshot.GitSnapshotError, indexer.git_snapshot.STAGED_REVISION, indexer.git_snapshot.TreeDelta, indexer.git_snapshot.TreeEntry, indexer.git_snapshot.WORKTREE_REVISION, indexer.go_parser.parse_go_file, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.java_parser.parse_java_file, indexer.js_parser.parse_js_file, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.repo_registry.RepoRegistry, indexer.repo_registry._get_repo_lock, indexer.repository_embedding.ConfiguredEmbeddingProvider, indexer.repository_index.EnrichmentReport, indexer.repository_index.IndexScope, indexer.repository_index.RepositoryIndex, indexer.repository_index.RepositoryIndexError, indexer.repository_index.SearchHit, indexer.repository_index.SearchRequest, indexer.repository_index.SymbolRecord, indexer.repository_index.SyncReport, indexer.repository_index.SyncRequest, indexer.repository_projection.write_repository_projection, indexer.repository_service.RepositoryService, indexer.repository_service.default_branch, indexer.repository_store.RepositoryStore, indexer.repository_store.RepositoryStoreError, indexer.rest_api.create_app, indexer.retrieval, indexer.retrieval._extract_error_frames, indexer.retrieval._extract_error_terms, indexer.retrieval._extract_graphql_operations, indexer.retrieval._extract_http_paths, indexer.retrieval._freshness_risks, indexer.retrieval._git_diff, indexer.retrieval._has_code_changes, indexer.retrieval._has_config_changes, indexer.retrieval._infer_entry_point_kind_from_hit, indexer.retrieval._is_test_path, indexer.retrieval._limit_list, indexer.retrieval._looks_like_client_symbol, indexer.retrieval._looks_like_entry_point, indexer.retrieval._natural_language_alias_score, indexer.retrieval._node_edges, indexer.retrieval._normalize_source_signature, indexer.retrieval._parse_diff_changed_files, indexer.retrieval._parse_diff_new_ranges, indexer.retrieval._parse_json_list, indexer.retrieval._repo_nodes_for_graph, indexer.retrieval._stable_id_moves, indexer.retrieval._symbols_for_changed_files, indexer.retrieval.agent_capabilities_manifest, indexer.retrieval.agent_protocol_bundle, indexer.retrieval.change_plan, indexer.retrieval.change_set, indexer.retrieval.coverage_map, indexer.retrieval.cross_repo_graph, indexer.retrieval.diagnose_index, indexer.retrieval.find_tests_for_symbol, indexer.retrieval.get_edit_context, indexer.retrieval.get_index_status, indexer.retrieval.get_source_context, indexer.retrieval.impact_analysis, indexer.retrieval.index_diff_report, indexer.retrieval.list_entry_points, indexer.retrieval.locate_from_error, indexer.retrieval.post_edit_verify, indexer.retrieval.pre_edit_check, indexer.retrieval.resolve_symbol, indexer.retrieval.search_code, indexer.retrieval.stable_symbol_id, indexer.retrieval.trace_call, indexer.retrieval.truncate_documents, indexer.ruby_parser.parse_ruby_file, indexer.rust_parser.parse_rust_file, indexer.task_store.TaskStore, indexer.utils._node_name, indexer.utils._node_text, indexer.utils._rel, indexer.utils.load_env_file, indexer.utils.resolve_api_key, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki._atomic_write_text, indexer.wiki._jinja_env, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.sanitize_group_label, indexer.wiki.write_index, indexer.wiki.write_page, jinja2.Environment, jinja2.FileSystemLoader, json, logging, math, mcp.server.fastmcp.FastMCP, openai.APIConnectionError, openai.APITimeoutError, openai.OpenAI, openai.RateLimitError, os, pathlib.Path, pathlib.PurePosixPath, random, re, shutil, sqlite3, starlette.applications.Starlette, starlette.middleware.Middleware, starlette.middleware.base.BaseHTTPMiddleware, starlette.requests.Request, starlette.responses.HTMLResponse, starlette.responses.JSONResponse, starlette.routing.Route, starlette.staticfiles.StaticFiles, subprocess, tempfile, threading, time, tomli_w, tomllib, tree_sitter.Language, tree_sitter.Parser, tree_sitter_go, tree_sitter_java, tree_sitter_javascript, tree_sitter_ruby, tree_sitter_rust, tree_sitter_typescript, typing.Callable, typing.Iterable, typing.Iterator, typing.Protocol, typing.Sequence, urllib.error, urllib.parse, urllib.request, uuid, uvicorn, warnings
## Entry Points
- `agent_schema`
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
- `embed_query`
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
- `main`
- `EmbeddingProvider`
- `register_repo`
- `task_status`
- `validate_repo`
- `sync_repo`
- `sync_all_branches`
- `update_repo_and_sync`
- `unregister_repo`
- `agent_protocol`
- `agent_capabilities`
- `agent_schema`
- `stable_symbol_id_endpoint`
- `index_status`
- `list_repos`
- `health`
- `repo_detail`
- `wiki_page_content`
- `update_repo_meta`
- `multi_repo_skill`
- `webhook_by_name`
- `resolve_wiki_page_path`
