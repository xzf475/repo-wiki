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

- **301 symbols** across **32 files** — indexed 2026-04-28 @ `5ead16e2`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a multi-language code indexer and semantic retrieval engine. It parses source code into AST nodes via language-specific parsers (indexer/ast_parser.py, rust_parser.py, java_parser.py, ruby_parser.py, js_parser.py, go_parser.py), groups nodes into pages (grouper.py), generates embeddings (embedding.py), and stores them in a vector store (vector_store.py). Indexing state is managed by Manifest (manifest.py) with git integration (git.py) for incremental updates, and a REST API (rest_api.py) and MCP server (mcp_server.py) expose search, symbol tracing, and context retrieval.
## Key Request Flows
- CLI index command → indexer/cli.py → git.py (clone/pull) → indexing.py → language-specific parsers → grouper.py → manifest.py → embedding.py → vector_store.py → wiki.py
- REST API search → indexer/rest_api.py → retrieval.py → vector_store.py (query) → return results with page context
- MCP trace_call_tool → indexer/mcp_server.py → retrieval.py → indexing.py → parser node cross-references → call graph response
- Webhook sync → indexer/hooks.py → git.py (pull) → _index_page → parsers → grouping → embedding → update manifest and vector store
- LLM deep enrichment → indexer/llm.py → retrieval.py (get symbol context) → LLM generates agent hints → update page content in wiki.py

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | main, init, status, hook, hook_install |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- File hash (SHA256) determines re-parse need; unchanged files use cached ASTNode JSON to avoid redundant computation.
- Embedding API key resolved via environment variable or .env file; if absent, embedding step silently skips (nodes stored without vectors).
- ASTNode cache is stored in `.indexer/cache/<file_hash>.json`; cache directory auto-added to `.gitignore` on `init`.
- Language-specific parser selection is based on file extension (e.g., `.py` → python parser, `.js` → js_parser); unsupported extensions are ignored by `_is_indexable`.
- Indexable files filtered by `ignore` globs in `.indexer.toml`; dot-directories and common build artifacts excluded by default.
- Vector store (ChromaDB) is ephemeral per index run; wiki markdown pages are the persistent searchable artifact, not the vector DB.
**tests**
- Cached nodes are stored as pickled files keyed by file path; cache is invalidated only on file modification time, not content hash, so timestamps must be reliable across runs.
- Docstring extraction differs per language: Java parses Javadoc comments, Python uses docstring statements, Ruby and Rust use doc comments (///, /**). The parser must strip leading `*` and whitespace uniformly.
- Rust trait methods are emitted as separate `Node` objects with type `trait_method` and a parent reference to the trait node; they are not nested inside the trait's method list.
- Imports are always emitted as synthetic `Node` objects of type `Import`; they do not carry docstrings or calls, only a `name` field (the fully qualified import path) and a `line` number.
- Java enums and interfaces are parsed as `class` nodes with a `kind` field set to `enum` or `interface`; the same unified `Node` structure is used, not separate subtypes.
- Ruby module nodes are top‑level constructs; inside them, classes and methods are nested by line‑range rather than as child references — consumers must flatten manually if needed.

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