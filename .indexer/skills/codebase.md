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

- **642 symbols** across **50 files** — indexed 2026-08-22 @ `3b9d2373`
- Wiki: `wiki/` — 3 page(s)
- Index: `.indexer/state/repository-index.sqlite3` — current transactional generation

## System Overview

repo-wiki:jame/artifact-branch-index generation 3 at tree 3b9d23732ec22a3698c22cab765f4d12e5c33725

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/__init__.py, indexer/agent_context.py, indexer/agent_contracts.py, indexer/agent_diagnostics.py, indexer/agent_diff.py, indexer/agent_graph.py, indexer/agent_protocol.py, indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/git_ops.py, indexer/git_snapshot.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/java_parser.py, indexer/js_parser.py, indexer/mcp_server.py, indexer/repo_registry.py, indexer/repository_benchmarks.py, indexer/repository_embedding.py, indexer/repository_index.py, indexer/repository_projection.py, indexer/repository_service.py, indexer/repository_store.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/search_eval.py, indexer/task_store.py, indexer/utils.py, indexer/wiki.py | resolve_symbol, list_entry_points, locate_from_error, agent_schema, stable_symbol_id |
| [tests](../wiki/tests.md) | tests/__init__.py, tests/test_agent_cli.py, tests/test_api_contracts.py, tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_performance_baseline.py, tests/test_repository_adapters.py, tests/test_repository_index.py, tests/test_runtime_safety.py, tests/test_wiki.py | test_agent_capabilities_cli_outputs_contract, test_agent_schema_cli_outputs_openapi_contract, test_agent_context_cli_requires_symbol_id, test_agent_capabilities_all_tools_have_schemas, test_core_tool_contract_top_level_keys |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, UserProfile.getDisplayName |

## Workflow — How to Answer Questions About This Codebase

Follow these steps in order. Do not skip ahead to reading source files.

1. **Orient** — Read `wiki/INDEX.md` first. It has the system overview, module map, and cross-cutting flows.

2. **Locate the module** — Match the question to a wiki page from the table above. Read that page only; do not read unrelated pages.

3. **Look up symbols** — Component IDs follow `relative/path.py::ClassName.method_name`. Find the relevant ID in the wiki page's Key Symbols table and read its description there.

4. **Trace calls without reading source** — Use the `## Relationships → Called by` section on the wiki page to trace callers. Use `## Relationships → Calls` to trace callees.

5. **Read source only when necessary** — Once you know the exact file and line range from the wiki or `search_symbols_tool`, read only that range. Do not read whole files speculatively.

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
| How does a request flow end-to-end? | Wiki relationships, then `trace_call_tool` |
| What are the gotchas or invariants? | Wiki and exact source ranges |
| What is the exact implementation? | Source — use line_start/line_end from search results |
| Is X tested? | Source — check test files directly |

## Component ID Format

```
relative/path.py::ClassName.method_name   ← method
relative/path.py::ClassName               ← class
relative/path.py::function_name           ← top-level function
```

## Generation Lookup

To locate symbols and their Wiki projection:
```
search_symbols_tool(query="path/to/file.py")
```

To inspect freshness and the visible generation:
```
get_index_status_tool()
```

## Edge Cases

- **Symbol not in wiki** — The index covers files tracked at index time. If a symbol is missing, it was added after the last `repo-wiki run`. Tell the user and read the source file directly.
- **Wiki page missing** — Fall back to structural search and an exact source range. Note the projection gap to the user.
- **Ambiguous name** — If multiple symbols share a name, list all matching component IDs and ask the user which they mean before proceeding.
- **Question spans multiple modules** — Read each relevant wiki page in turn. Do not conflate descriptions from different pages.