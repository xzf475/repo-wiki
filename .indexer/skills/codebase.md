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

- **77 symbols** across **2 files** — indexed 2026-05-09 @ `58ec64b2`
- Wiki: `wiki/` — 3 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a code indexer and retrieval engine that parses source repositories (Python, Java, Ruby, Rust, etc.) using language-specific AST parsers, extracts symbols and relationships, generates embeddings via an LLM (Litellm), and stores them in a vector store with a manifest-based file tracking system. The indexer module orchestrates pipeline steps (parse, describe, embed, store) while the retrieval module supports symbol search, call tracing, and context fetching through REST and MCP APIs, backed by a task store and repo registry for concurrency-safe operations. Configuration is managed via TOML, and git integration handles cloning, branch tracking, and webhook-triggered re-indexing.
## Key Request Flows
- Repo registration → git clone → branch discovery → parse files → describe nodes/files → embed → upsert vectors → write manifest → build wiki pages
- Search query → retrieval.query → vector store similarity search → enrich with context (symbol descriptions, call graphs) → return results via REST or MCP
- Trace call → resolve symbol → retrieve call graph (callers/callees) → expand with depth limit → fetch source context → return enriched trace
- Webhook event → git pull/fetch → detect changed files → reindex changed files → update vectors and manifest → notify via task store
- Multi-repo skill → iterate registered repos → run search/trace across each → aggregate results → return combined response

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/ast_parser.py, indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/go_parser.py, indexer/grouper.py, indexer/hooks.py, indexer/indexing.py, indexer/java_parser.py, indexer/js_parser.py, indexer/llm.py, indexer/manifest.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/retrieval.py, indexer/ruby_parser.py, indexer/rust_parser.py, indexer/utils.py, indexer/vector_store.py, indexer/wiki.py | _get_type_name, describe_nodes_batch, describe_nodes, describe_files, _describe_files_chunk |
| [tests_fixtures](../wiki/tests_fixtures.md) | tests/fixtures/sample_java/App.java, tests/fixtures/sample_py/auth.py, tests/fixtures/sample_ruby/app.rb, tests/fixtures/sample_rust/lib.rs | App, App.addUser, App.getUserCount, UserProfile, getDisplayName |
| [tests](../wiki/tests.md) | tests/test_ast_parser.py, tests/test_config.py, tests/test_grouper.py, tests/test_manifest.py, tests/test_p1_fixes.py, tests/test_wiki.py | test_parse_returns_nodes, test_function_node, test_method_node, test_class_node, test_docstring_extracted |
## Critical Constraints (read before editing)
**indexer**
- AST caching relies on file content hash (sha256); any byte-level change (even whitespace) invalidates cache, but docstring/extracted fields cache persists across runs via save_cached_nodes/load_cached_nodes.
- Embedding API calls use a batch size (likely ~20) and random key rotation via uniform() over sorted keys to avoid rate limit issues; missing or invalid keys log warning but do not raise.
- Git operations (`_run`) suppress stderr and return '' on failure (not None), but changed_files_since can raise ValueError on invalid ref; all_tracked_files and staged_files return empty list on error.
- Each language parser handles only its own syntax; unsupported constructs produce empty ASTNode (no errors); the general parse_file dispatches by extension and falls back to AST parser (python-only).
- Enforced 1-per-user limit at creation? Not present; but vector store config may assume a singleton collection per codebase (no concurrent writes).
- Config fields default to None if missing; _apply_env_field replaces only if env var is set, but _env_int logs warning on parse failure and returns None, not a fallback default.
**tests**
- Tests use next() on parse_file generator to get first node; this assumes the first node is the top-level symbol (e.g., class, function) – order must be deterministic.
- Assertions rely on endswith for name checks because sample code uses fully qualified names (e.g., 'MyClass'); exact match would be brittle across language conventions.
- The cache test does not verify node content equivalence, only length; deeper equality is assumed from serialization format consistency.
- Language-specific tests each contain inline sample code that must be kept in sync with parser capabilities; addition of a new language requires a new test suite.
- The 'any' call in many tests means no assumption on node ordering within the returned list – parser may return nodes in arbitrary order (e.g., depth-first vs breadth-first).
- test_docstring_extracted uses next() on parse_file then accesses doc attribute; this assumes the first returned node has a docstring – relies on sample code having docstring on first symbol.

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