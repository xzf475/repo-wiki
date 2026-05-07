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

- **392 symbols** across **11 files** — indexed 2026-05-07 @ `184baff1`
- Wiki: `wiki/` — 2 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a code indexing service that clones git repositories, parses source files, generates embeddings via an embedding API, and stores vector representations alongside metadata (symbols, call graphs) in a vector store. Main modules are `indexer/cli.py` (CLI interface), `indexer/git.py` (git operations), `indexer/indexing.py` (indexing pipeline), `indexer/embedding.py` and `indexer/llm.py` (external API calls), `indexer/vector_store.py` (vector CRUD), `indexer/rest_api.py` (REST endpoints), and `indexer/mcp_server.py` (MCP tools). The `TaskStore` and `RepoRegistry` manage async tasks and repository metadata. It supports multiple repositories, branches, and provides search, trace, and context tools via both REST and MCP.
## Key Request Flows
- CLI/API register_repo → RepoRegistry.register → git clone → _index_page → describe_nodes_batch → embedding API call → vector_store.upsert_nodes → manifest update
- search_symbols_tool (REST or MCP) → parse query → vector_store.search (with branch filter) → return symbol results
- trace_call_tool → expand call graph from indexed edges → vector_store.query for caller/callee nodes → return context chain
- webhook_by_name → validate payload → sync_repo → git fetch + detect changed files → reindex changed files → vector_store.delete_by_files + upsert → manifest update
- deep_enrich_page → LLM API call for descriptions/tags → update node metadata → re-embed (optional) → vector_store.update nodes

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/cli.py, indexer/config.py, indexer/embedding.py, indexer/git.py, indexer/indexing.py, indexer/llm.py, indexer/mcp_server.py, indexer/rest_api.py, indexer/utils.py, indexer/vector_store.py | main, init, status, hook, hook_install |
| [root](../wiki/root.md) | tests/test_p1_fixes.py | TestTaskStore, TestTaskStore.test_create_task, TestTaskStore.test_update_task, TestTaskStore.test_update_finished_sets_timestamp, TestTaskStore.test_update_nonexistent_task_noop |
## Critical Constraints (read before editing)
**indexer**
- API key resolution supports file-based secrets: if env var ends with '_FILE', its value is treated as a file path whose contents are read as the key.
- Embedding text is built only from node `signature` and `docstring` (not full source body) to avoid exceeding token limits of the embedding model.
- Configuration is loaded from a TOML file but each field can be overridden by environment variables (using `_env`, `_env_int` helpers) with no warning if the file is missing; defaults are set via dataclass field defaults.
- Vector store configuration has a `store_dir` that defaults relative to the repo root; the actual store driver is abstracted (e.g., dummy for testing, proper vector DB in production).
- Git operations assume `cwd` is a git repo; failures produce warnings and empty results, not exceptions, to allow graceful degradation in non-git directories.
**root**
- TaskStore.update on a nonexistent task silently returns (no-op, not an error).
- TaskStore.get returns None (not raises) for nonexistent task ID.
- RepoLock skip-lock acquisition does NOT release an already held lock; acquire() and release() are not called when skip=True and lock is held.
- Empty string in environment variable does not override existing config value (_apply_env preserves original).
- Git checkout failure in _run_rebuild_task_inner marks the task as failed (status set) before propagating or continuing.
- Manifest parsed from file: missing 'component_ids' defaults to empty list, missing 'hash' defaults to empty string, and unparseable JSON returns an empty dict (not a raise).

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