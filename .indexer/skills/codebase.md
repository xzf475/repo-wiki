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

- **481 symbols** across **23 files** — indexed 2026-05-11 @ `a62514d9`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The indexer is a service that indexes source code repositories into a searchable knowledge base. It uses language-specific AST parsers (e.g., js_parser, rust_parser) to extract symbols, calls, and docstrings, then builds wiki pages with cross-references. The indexed data is stored in a vector store for semantic search and a task store for tracking async rebuilds. A REST API and MCP server expose tools for repository registration, symbol search, call trace, and source context retrieval.
## Key Request Flows
- register_repo → RepoRegistry.register → git clone → parse candidates → indexing pipeline → vector store upsert → manifest save
- search_symbols_tool → REST API handler → retrieval.search_symbols → (embedding query → vector store search → return nodes)
- trace_call_tool → REST API handler → retrieval.trace_call → (AST cross-reference → recursive call graph expansion → return context)
- webhook sync → repo_registry.sync_repo → git fetch → changed files detection → re-parse changed files → incremental vector store update → manifest update
- MCP tool (e.g., get_source_context) → mcp_server handler → retrieval.get_source_context → AST node lookup → file lines extraction → formatted response

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cache.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/git_ops.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/repo_registry.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/task_store.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | _patched_method, search_symbols_tool, trace_call_tool, get_source_context_tool, list_repos |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- ASTNode.calls are extracted via static AST walk (walk); dynamic or indirect calls (e.g., via getattr) are NOT captured, leading to incomplete traces.
- grouper.density_group groups files by prefix density, not directory hierarchy; a file at a/b/c/d.py may be grouped with a/b/x/d.py if density of 'a/b/' is low, but not with a/e.py if 'a/' density is high.
- MCP server authentication uses _MCPAuthMiddleware which compares tokens with compare_digest; only a single static API token is supported (no multi-user or scoped tokens).
- Hooks (install_hook, remove_hook) modify .git/hooks directly as shell scripts; they assume a Unix-like environment and will fail on Windows without WSL.
- The ast_parser uses tree-sitter for non-Python languages (Ruby, Rust, Java, Go, JS) but falls back to Python's ast module for .py files; parsing failures on malformed code silently return empty ASTNode instead of raising.
- Vector store operations (vector_store.py) are not transactional; concurrent indexing jobs may produce partial or duplicated vectors if not locked externally.
**tests_fixtures**
- TokenValidator.refresh() assumes `sign_payload` is a callable in scope; no fallback or error handling is provided (minimal test stub).
- Router.initialize accepts no arguments; routes are stored as a hash without thread safety—single-threaded test context only.
- Java App.getUserCount() returns the raw size of the ArrayList; no null or duplicate checks on addUser (duplicate names allowed).
- Rust age_difference(a, b) is a pure function that returns absolute difference; it does not handle negative ages or overflow (u8).
- The Rust Status enum has no default or unknown variant; any serialization of an uninitialized User would panic (no TryFrom/Default).
- Ruby parse(str) calls strip on the input but does not handle nil—calling parse(nil) would raise NoMethodError.
**tests**
- `parse_file` selects parser based on file extension; unsupported extensions raise an exception, tested implicitly by skipping other languages.
- Cache serialization uses JSON; node objects must be serializable (e.g., `Node` is a dataclass with simple fields), and `load_cached_nodes` reconstructs them without accessing the original code.
- The docstring extraction test (`test_docstring_extracted`) assumes the first node in the returned list carries the docstring; it fails if node ordering changes.
- Import extraction tests (`test_imports_extracted`) use `isinstance` with a tuple of node types, requiring the exact types (e.g., `ImportNode`, `ImportFromNode`) to match.
- All inline sample code is embedded as raw strings in test functions; modifications to parser behavior may require updating samples that rely on specific node order or attribute values.
- The cache round-trip test uses `TemporaryDirectory` to ensure cleanup; it assumes the cache directory is writable and non‑existent initially.

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