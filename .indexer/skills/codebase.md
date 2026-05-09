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

- **372 symbols** across **8 files** — indexed 2026-05-09 @ `f3c2a981`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a multi-language code indexer that ingests git repositories, parses source files into AST nodes (via language-specific parsers in `indexer/ast_parser.py`, `go_parser.py`, `java_parser.py`, `js_parser.py`, `ruby_parser.py`, `rust_parser.py`), generates LLM-based descriptions and embeddings (`indexer/embedding.py`, `indexer/llm.py`), and stores results in a vector database (`indexer/vector_store.py`) alongside rendered wiki pages (`indexer/wiki.py`). A manifest layer (`indexer/manifest.py`) tracks file hashes and component IDs, while the grouper (`indexer/grouper.py`) decides folder-level page organization. The system exposes a CLI (`indexer/cli.py`), a REST API (`indexer/rest_api.py`), and an MCP server (`indexer/mcp_server.py`) for search, symbol tracing, and context retrieval, with task management via `TaskStore` and `RepoRegistry`.
## Key Request Flows
- Register repo via API/CLI → `register_repo` → clone git → `_index_page` → parse files with `ast_parser` → `compute_ast_sig` → upsert nodes to vector store → build wiki pages via `_build_page`
- Search query → REST API `/search` or MCP `search_symbols_tool` → `embed_query` → vector store `search` → return symbol nodes with context
- Trace call → MCP `trace_call_tool` → `expand_with_call_graph` → retrieve caller/callee chain from vector store → return full source context
- Git webhook → `webhook_by_name` → trigger `sync_repo` → detect changed files → `upsert_nodes` (new) → `delete_by_files` (removed) → rebuild manifest
- Init or reindex cascade: `rebuild_repo` → `rebuild_all_branches` → `_run_all` → for each file: parse → enrich (LLM) → embed → upsert → write wiki pages

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | main, init, status, hook, hook_install |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- AST parsing results are cached on disk using SHA256 hashes of file bytes; cache invalidated only when file content changes (not on timestamp).
- Config file is written atomically using `NamedTemporaryFile` + `replace` to avoid partial writes.
- The `_is_indexable` function uses **fnmatch** patterns; files outside tracked language extensions are silently skipped during indexing.
- Embedding API key resolution falls back to `.env` file parsing; if neither environment variable nor `.env` contains `OPENAI_API_KEY`, the client creation will fail at runtime.
- The `parse_file` dispatcher only handles `.java`, `.js`, `.rb`, `.py`, `.go`, `.rs`; other file types are ignored (no generic fallback).
- Vector store is ephemeral per repository; the REST API serves multiple repos by aggregating separate vector stores in a directory (`repos_path`).
**tests_fixtures**
- Java App's internal `users` list (ArrayList) is not thread-safe; concurrent addUser calls may corrupt state without external synchronization.
- Python TokenValidator.refresh relies on `sign_payload` which assumes a pre‑loaded private key; no key rotation logic is present in the module.
- Ruby Router.dispatch matches routes by key equality (hash lookup); no wildcard or parameterised path support is exposed.
- Rust User.age_difference uses `abs` internally; caller must ensure no overflow on i32 age values (though unrealistic, may panic on extreme inputs).
- Python `require_auth` decorator calls `func` directly without any retry or fallback; any exception from the guarded function propagates unhandled.
- Rust User.to_json returns a simple string without error handling; serialization failure (e.g., non‑UTF‑8) is not indicated to caller.
**tests**
- Each source file must produce at least one node; parse_file does not handle empty files gracefully (returns empty list).
- Docstrings in Java must end with a period (asserted by test_java_javadoc_extracted); other languages have no such requirement.
- Cache roundtrip is tested only for Python nodes; other languages rely on general parse test coverage.
- Imports list is guaranteed to contain only strings (enforced via isinstance check per language).
- Rust enum and type alias node type names end with '_enum' and '_type_alias' respectively; trait method spec is a distinct node type.
- Ruby function and module nodes are type-checked via name ending with '_function' or '_module' (not present in Python/Java).

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