---
name: codebase
description: >
  Navigate this codebase. Activates when the user asks about code structure,
  where a function or class lives, how a module works, who calls a method,
  what a file does, how a request flows end-to-end, what changed, or where
  to make an edit. Trigger phrases include: "where is", "how does X work",
  "what does X do", "find the code for", "which file", "who calls", "trace
  the flow", "show me how", "explain the architecture", "what module",
  "read the source", "navigate the repo", "look at the codebase",
  "understand the code". Do NOT activate for general programming questions
  unrelated to this specific repo, writing new code from scratch, or tasks
  that require no codebase knowledge.
---

# Codebase Navigation

This repo is indexed. **Check the wiki before reading any source file.**
The wiki captures structure, relationships, and constraints in a fraction of the tokens.

## Stats

- **305 symbols** across **2 files** — indexed 2026-07-27 @ `5af1c57a`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a multi-language code indexer that parses source files into AST nodes, extracts symbols, calls, and entry points, then embeds them into a vector store for semantic retrieval. Core modules include `ast_parser`, `indexing`, `embedding`, `vector_store`, `manifest`, `wiki`, and `grouper` for building a structured knowledge base; the `agent_context`, `agent_contracts`, `agent_diff`, `agent_graph`, and `agent_diagnostics` modules expose a suite of agent tools (e.g., `search_symbols_tool`, `impact_analysis_tool`, `change_plan_tool`) via both a REST API (`rest_api`) and an MCP server (`mcp_server`). Git operations (`git`, `git_ops`), task management (`task_store`), and repo registry (`repo_registry`) handle lifecycle and synchronization. The architecture is designed to support AI agents in understanding, editing, and verifying changes across repositories.
## Key Request Flows
- Repo registration → `register_repo` → `run_rebuild_task` → `git clone` → `indexing` → `ast_parser` → `embedding` → `vector_store.upsert_nodes` → `manifest.save` → `wiki.build_page`
- User query (search symbol) → `search_symbols_tool` → `retrieval.do_search` → `vector_store.query` → `agent_context.resolve_symbol` → `agent_context.get_source_context`
- Edit flow: `pre_edit_check_tool` → `git_ops.changed_files_since` → `impact_analysis_tool` → `agent_graph.expand` → `change_plan_tool` → `agent_diff.generate_diff` → `post_edit_verify_tool` → `agent_diff.apply_diff`
- Error diagnosis: `locate_from_error_tool` → `agent_graph.locate_by_stack_trace` → `resolve_symbol_tool` → `get_edit_context_tool` → `agent_diagnostics.diagnose_index`
- Cross-repo dependency: `cross_repo_graph_tool` → `agent_graph.cross_repo_links` → `repo_registry.get` → `vector_store.query` across repos → `manifest.stable_symbol_id`

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/agent_context.py, indexer/agent_contracts.py, indexer/agent_diagnostics.py, indexer/agent_diff.py, indexer/agent_graph.py, indexer/ast_parser.py, indexer/cache.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/git_ops.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/repo_registry.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/task_store.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | main, init, status, agent, agent_context |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_agent_cli.py, tests/test_agent_context.py, tests/test_agent_e2e.py, tests/test_api_contracts.py, tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- Embedding model is configured via `EmbeddingConfig`; changing it invalidates all stored embeddings and requires a full re-index.
- `compute_hash_short` uses first 8 hex chars of SHA256; collisions are practically improbable for file-level change detection but not guaranteed.
- AST caching uses atomic writes to avoid partial corruption, but the cache is not synchronized across processes — concurrent CLI runs may overwrite.
- Stale file detection relies on git diff against HEAD; untracked files are not considered unless staged.
- Agent `change_plan` requires LLM availability; if LLM fails, it falls back to a heuristic structural plan but may miss semantic implications.
- `agent_diff` expects unified diff format from git; non-standard diffs (e.g., from `--no-index`) may cause parsing failures.
**tests_fixtures**
- Java `UserProfile` is an interface with no implementing class; any code that attempts to instantiate it will fail at runtime, but the analyzer must still extract its method signatures (`getDisplayName`, `getRole`).
- The `require_auth` decorator (Python) returns the wrapper function without actually performing authentication; it is a structural test for decorator detection, not a functional security mechanism.
- Ruby `Router#initialize` has an empty argument list, but the `add_route` method is never called inside the fixture; the analyzer must infer routes from static registration only, not from runtime execution.
- Rust `UserResult` is a type alias for `Result<User, String>`, but nowhere in the code is it used; it exists solely to test type alias symbol extraction.
- The `parse` function (Ruby) calls `strip` on its input but does not check for nil; an edge case that the analyzer must handle gracefully (no crash on missing string method detection).
- `age_difference` (Rust) is a public function that takes two `User` references but is never called internally; the analyzer must still record it as a callable symbol with no outgoing calls.
**tests**
- Tests use temporary directories (TemporaryDirectory) and do not depend on external resources; they are fully self-contained.
- The cache test (test_cache_roundtrip) verifies that save_cached_nodes and load_cached_nodes are inverses, critical for performance but fragile if serialization format changes.
- FastAPI and Click entry point detection relies on decorator patterns (e.g., @app.get, @app.route, @click.command); changes in decorator syntax may break detection.
- Multi-language support means each language has its own parser (likely via tree-sitter or custom logic); tests must cover all supported languages to avoid regressions.
- The test for API contracts (test_api_contracts.py) likely validates JSON output against a schema; this contract test must be updated when output format changes.
- The p1_fixes test suite is for regression tests of previously fixed bugs; these tests should be run before any release to ensure no reintroduction.

## Workflow — How to Answer Questions About This Codebase

Follow these steps in order. Do not skip ahead to reading source files.

1. **Orient** — Read `wiki/INDEX.md` first. It has the system overview, module map, and cross-cutting flows.

2. **Locate the module** — Match the question to a wiki page from the table above. Read that page only; do not read unrelated pages.

3. **Look up symbols** — Component IDs follow `relative/path.py::ClassName.method_name`. Find the relevant ID in the wiki page's Key Symbols table and read its description there.

4. **Trace calls without reading source** — Use the `## Relationships → Called by` section on the wiki page to trace callers. Use `## Relationships → Calls` to trace callees.

5. **Read source only when necessary** — Once you know the exact file and line range from the manifest or wiki, read only that range. Do not read whole files speculatively.

6. **Answer with specifics** — Include the component ID, file path, and line range (if known) in your answer so the user can navigate directly.

## Output Format

- Always name the specific file and component ID when identifying where code lives.
- For call traces, show the chain: `A → B → C`, one line per hop.
- For architecture questions, describe the flow in prose then list the files involved.
- Keep answers concise. Do not dump raw wiki content — summarise what is relevant.
- If a question requires reading source, state which file and lines you are about to read before reading them.

## When to Use Wiki vs Source

| Question type | Use |
|--------------|-----|
| What does X do? | Wiki — Key Symbols table |
| Who calls X? | Wiki — Relationships → Called by |
| What does this module own? | Wiki — Modules table |
| How does a request flow end-to-end? | Wiki — Data Flows section (if --deep indexed) |
| What are the gotchas or invariants? | Wiki — Design Constraints section (if --deep indexed) |
| What is the exact implementation? | Source — use line_start/line_end from manifest |
| Is X tested? | Source — check test files directly |

## Component ID Format

```
relative/path.py::ClassName.method_name   ← method
relative/path.py::ClassName               ← class
relative/path.py::function_name           ← top-level function
```

## Manifest Lookup

To find which wiki page covers a file:
```
.indexer/manifest.json → files["path/to/file.py"] → wiki_page
```

To find all symbols in a file:
```
.indexer/manifest.json → files["path/to/file.py"] → component_ids
```

## Edge Cases

- **Symbol not in wiki** — The index covers files tracked at index time. If a symbol is missing, it was added after the last `repo-wiki run`. Tell the user and read the source file directly.
- **Wiki page missing** — If a wiki page linked from the index does not exist, fall back to the manifest and source. Note the gap to the user.
- **Ambiguous name** — If multiple symbols share a name, list all matching component IDs and ask the user which they mean before proceeding.
- **Question spans multiple modules** — Read each relevant wiki page in turn. Do not conflate descriptions from different pages.