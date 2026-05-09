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

- **65 symbols** across **1 files** — indexed 2026-05-09 @ `d9fbb8bc`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a multi-language code indexer and retrieval engine built in Python. It consists of an **indexer** package that parses source files (via language-specific parsers like `ast_parser`, `go_parser`, `java_parser`, `js_parser`, `ruby_parser`, `rust_parser`), groups nodes, computes embeddings (`embedding.py`), and stores them in a vector database (`vector_store.py`). A **REST API** (`rest_api.py`) and **MCP server** (`mcp_server.py`) expose tools such as `search_symbols_tool`, `trace_call_tool`, and `get_source_context_tool`. Repository lifecycle (register, sync, rebuild) is managed by the `RepoRegistry` and `TaskStore` modules, with file state tracked in `manifest.py` and wiki pages generated via `wiki.py`. The **CLI** (`cli.py`) provides `init`, `status`, `hook`, and `serve` commands, while `config.py` handles defaults and validation.
## Key Request Flows
- register_repo → RepoRegistry.register → git clone → discover branches → indexing pipeline (parse → group → embed → vector store) → manifest update → wiki build
- search_symbols_tool (MCP or REST API) → retrieval.search_symbols → vector_store.query (with branch filter) → return ranked node results
- trace_call_tool (MCP or REST API) → retrieval.trace_call → node cross-reference (calls_in/called_by aggregation) → resolve context with vector_store and expand depth-limited call graph
- webhook_by_name (REST API) → sync_repo → git fetch/checkout → re-index changed files → update vector store and manifest
- TaskStore.create/get/update/cleanup → async pipeline (e.g., reindex_repo) → progress tracking via task status → RepoRegistry thread-safe operations with repo locks

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | main, init, status, hook, hook_install |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- Only files tracked by git are indexed; untracked or ignored files are skipped (enforced by `_is_indexable` + git ls-files).
- Caching uses SHA256 hash of raw file bytes; cache is invalidated only when content changes, not on metadata changes like timestamps.
- Each language parser is a separate module (e.g., `js_parser.py`, `rust_parser.py`); adding a new language requires implementing `parse_<lang>_file` and registering in `parse_file` dispatch.
- The `grouper.py` uses density-based clustering (likely HDBSCAN) on embeddings to group symbols; this is non-deterministic and may produce different groupings on re-runs if the seed is not fixed.
- The vector store is ephemeral by default (in-memory or local file) unless configured for a cloud backend; `load_existing_nodes` only restores cached AST nodes, not embeddings.
- The pre-commit hook runs on `git commit` but does not block the commit if indexing fails; the `run` command must be invoked manually to rebuild the entire index if the hook is not used.
**tests_fixtures**
- Java App does not enforce uniqueness; duplicate UserProfile objects can be added to the same list.
- Python require_auth decorator does not handle exceptions from func; wrapper will propagate any error from the original function.
- Ruby Router.dispatch assumes stored handler responds to `call`; no type checking on route registration.
- Rust age_difference returns an i32 difference; if ages are equal returns 0, but overflow for large i32 values is not handled.
- Rust User.to_json serializes fields in declaration order (name, age, status); order is not guaranteed by the ToJson trait signature.
- Python TokenValidator.refresh calls sign_payload which is not defined in this module; must be provided externally.
**tests**
- All parser tests use inline source strings or TemporaryDirectory—no external file dependencies to ensure isolation and speed.
- Java/Ruby parser tests require tree-sitter parsers; they must skip (not fail) via pytest marks if parsers are missing.
- Cache tests must clean up serialized files after each run to avoid cross-test contamination.
- test_p1_fixes are regression tests; they are expected to fail if the corresponding bug fix is accidentally reverted.
- Manifest tests raise ValueError on empty or malformed input; the Config test ensures missing keys fall back to defaults without crashing.
- Wiki tests generate output into a temporary directory that is recreated before each test to guarantee a clean slate.

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