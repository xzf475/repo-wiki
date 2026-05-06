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

- **351 symbols** across **21 files** — indexed 2026-05-06 @ `23da6a82`
- Wiki: `wiki/` — 2 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

This system is a code indexing and semantic search platform that parses source code across multiple languages (Python, Java, JavaScript, Ruby, Rust) using AST parsers in `indexer/ast_parser.py`, `java_parser.py`, `js_parser.py`, `ruby_parser.py`, and others. Extracted symbols, calls, and relationships are enriched with embeddings via `indexer/embedding.py` and stored in a vector store (`indexer/vector_store.py`) alongside a manifest (`indexer/manifest.py`) for incremental updates. The system exposes a REST API (`indexer/rest_api.py`) and an MCP server (`indexer/mcp_server.py`) for search, trace, and code context tools, with background tasks managed by a `TaskStore` and repo state tracked by a `RepoRegistry`. It integrates with Git (via `indexer/git.py` and hooks in `indexer/hooks.py`) to monitor file changes and trigger reindexing.
## Key Request Flows
- Git hook → hooks.py → git.py (diff detection) → indexing.py (reindex) → AST parsers → embedding.py → vector_store.py → manifest.py update
- REST API request (/search) → rest_api.py → retrieval.py (embed query) → vector_store.py (nearest neighbors) → return results to API
- MCP tool call (search_symbols) → mcp_server.py → retrieval.py → vector_store.py + AST parsers for source context → return tool response
- CLI init → cli.py → config.py (load settings) → indexer initialization → embedding model load → vector store create → manifest check
- REST API async task (register repo) → rest_api.py → TaskStore.create → background worker → indexing.py (clone/checkout via git.py) → AST parse → embedding → vector_store insert → manifest record → TaskStore.update(finished)

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | main, init, status, hook, hook_install |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_p1_fixes.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- Parsing is cached by truncating file SHA256 to first 8 hex chars; cache miss only on content change, not timestamp.
- Language-specific parsers are switched by file extension/name string matching inside `ast_parser.parse_file`, not by config or heuristics beyond the provided patterns.
- The pre-commit hook runs `indexer run` on every commit; if indexing fails, the commit still proceeds (hook is non-blocking).
- API key for embeddings is resolved in order: `OPENAI_API_KEY` env var > `.env` file in repo root > `config.toml`; missing key silences embedding but indexing proceeds.
- Vector store dimension must match embedding model output dimension; mismatch causes silent insert failures (no validation at config load).
- The manifest (`manifest.json`) is the source of truth for which files have been indexed; stale files are detected by comparing current git hash vs stored hash, not by file mtime.
**tests**
- Language detection is based on file extension; parsing a file with an unsupported extension may return an empty list (this is untested here but implied by the fixture-only approach).
- Cache serialization uses temporary directories; nodes must be JSON-serializable or picklable; the test only compares length, not deep equality.
- Docstring extraction heuristics differ per language: Python uses triple-quoted strings, Rust uses `///` comments, Java uses `/** */` blocks, Ruby uses `=begin`/`=end` or `#` comments—tests assert extraction for each.
- Import extraction returns a list of strings; for Java it includes package declarations, for Rust `use` statements, for Python `import`/`from`, for Ruby `require`/`include`—tested via `isinstance` and `len`.
- Node identity checks rely on `any` and `endswith` for name matching, implying nodes have a `.name` attribute that includes a type suffix or exact filename-derived name.
- The parser must handle multi-language files (e.g., Rust traits with method signatures, Ruby modules) consistently; tests for Rust trait method specs confirm that empty-bodies or signatures are still parsed as nodes.

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