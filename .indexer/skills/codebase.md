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

- **551 symbols** across **19 files** — indexed 2026-05-22 @ `34b839cf`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a multilingual code indexer and AI agent framework that ingests repositories (via git) across Python, Java, Ruby, Rust, Go, and JavaScript. It parses source into AST nodes (symbols, calls, imports), embeds them into a vector store, and generates per-module wiki pages with cross-reference graphs. The system exposes agent capabilities through a REST API and an MCP server (agent_context.py, retrieval.py, agent_graph.py), while managing indexing tasks via a TaskStore and repo state via a RepoRegistry. CLI (cli.py) and hooks (hooks.py) provide local integration, and the whole pipeline is driven by an indexing orchestrator (indexing.py) that coordinates parsers, caching, and manifest updates.
## Key Request Flows
- Indexing Flow: CLI/REST hook → repo_registry → git_ops (clone/fetch) → ast_parser (per language) → embedding → vector_store → wiki → manifest → task_store (status)
- Agent Context Query: MCP/REST (agent_context) → retrieval (search_symbols, trace_call) → vector_store + wiki → agent_graph (expand relations) → get_edit_context → return bundles (symbols, tests, files, status)
- Post-Edit Verification: agent_diff (diff parsing) → pre_edit_check → impact_analysis → change_plan → post_edit_verify → reindex pipeline → change_set (target+impact+tests)
- Repository Registration & Sync: CLI (register_repo / sync_repo) → repo_registry → git_ops (validate, clone) → task_store (create task) → indexing.py (full reindex, branch detection) → manifest + vector_store eviction → webhook callbacks
- Error Diagnosis Flow: locate_from_error (stack trace parse) → resolve_symbol → agent_protocol (bundle freshness) → diagnose_index (missing wiki/vector) → trigger reindex if stale

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/agent_context.py, indexer/agent_contracts.py, indexer/agent_diagnostics.py, indexer/agent_diff.py, indexer/agent_graph.py, indexer/ast_parser.py, indexer/cache.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/git_ops.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/repo_registry.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/task_store.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | _first_char_shard, _get_type_name, describe_nodes_batch, describe_nodes, describe_files |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_agent_cli.py, tests/test_agent_context.py, tests/test_agent_e2e.py, tests/test_api_contracts.py, tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_load_defaults, test_save_and_reload, test_partial_toml_uses_defaults, test_sparse_folders_merge_to_parent, test_dense_folder_gets_own_page |
## Critical Constraints (read before editing)
**tests_fixtures**
- Fixtures must have zero external dependencies (no imports beyond language standard library) to guarantee portability across test environments.
- All `calls` entries are string literals extracted from source; they may reference methods that do not exist in the fixture set (e.g., `sign_payload`), as the goal is to record syntactic calls, not resolve them.
- Java interface `UserProfile` and Rust trait `ToJson` define no implementation and serve only to verify the extractor recognizes interface/trait symbol types.
- Ruby's `parse` function calls `strip` (a String method) but that call is recorded as a raw string — the extractor does not distinguish built-in from user-defined calls.
- Rust `UserResult` type alias is included to ensure `type` symbols are captured alongside struct/enum/trait symbols.
- Symbol IDs are globally unique by prepending the file path; duplicate simple names (e.g., `getDisplayName` in Java vs Ruby) are allowed only across different files.
**tests**
- test_config functions use _clean_env/_restore_env to pop/restore specific env vars; they must be called in that order and are not idempotent if called outside test flow
- density_group expects input as list of (Path, file_count) tuples; hierarchy is determined by Path.relative_to and parent anchor logic; sparse means <=1 file per folder
- test_manifest hash test uses NamedTemporaryFile with delete=False; file remains until test ends; compute_hash reads entire file content
- test_api_contracts modifies Config attributes via setattr to create a synthetic agent_protocol_bundle; this mutates the global Config object and is not thread-safe
- test_wiki _make_node returns ASTNode with 'calls' and 'called_by' as lists; the symbols must be added via update() afterwards
- test_agent_cli uses CliRunner from click.testing; each test invokes a separate Click command group; output is captured as string and parsed with json.loads

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