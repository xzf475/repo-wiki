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

- **348 symbols** across **6 files** — indexed 2026-05-08 @ `16f0a7ed`
- Wiki: `wiki/` — 2 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a code indexing service that ingests, embeds, and searches code repositories via vector similarity. The `indexer` module contains a CLI (`cli.py`), a REST API (`rest_api.py`), an embedder (`embedding.py`), an indexer pipeline (`indexing.py`), and a vector store (`vector_store.py`). `TaskStore` manages asynchronous indexing jobs, and `RepoRegistry` persists repository metadata (branches, manifests). The service exposes endpoints for registration, sync, unregistration, and search, with all index mutations gated through task creation to ensure atomicity and lock correctness.
## Key Request Flows
- register_repo (CLI or API) → RepoRegistry.register → TaskStore.create → _run_register_task → clone repo → _index_page → embed → upsert_nodes (vector_store) → update manifest (RepoRegistry.update_meta)
- webhook_by_name (API) → sync_repo → TaskStore.create → sync_all_branches → reindex (indexing pipeline with stale node detection and incremental upsert)
- REST API search → embed_query (embedding) → vector_store.do_search (with branch filter) → return ranked results (including symbol context and call graph expansion)
- unregister_repo (CLI or API) → RepoRegistry.unregister → TaskStore.create → remove repo lock → delete_by_files (vector_store) → cleanup manifest and TaskStore entries
- rebuild_repo (CLI or API) → TaskStore.create → evict vector store client → rmtree clone dir → re-clone → re-index full pipeline (embedding batch, parallel description, vector upsert before manifest write)

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/cli.py, indexer/embedding.py, indexer/indexing.py, indexer/rest_api.py, indexer/vector_store.py | main, init, status, hook, hook_install |
| [root](../wiki/root.md) | tests/test_p1_fixes.py | TestTaskStore, TestTaskStore.test_create_task, TestTaskStore.test_update_task, TestTaskStore.test_update_finished_sets_timestamp, TestTaskStore.test_update_nonexistent_task_noop |
## Critical Constraints (read before editing)
**indexer**
- Symbol descriptions are cached per-file hash in `<cache_dir>/desc/` and merged on save; incremental runs skip re-generation but new descriptions are added, not overwritten, preserving previous descriptions if API fails.
- Embedding API calls use a uniform random delay (0.5–1.5s) between batches to respect rate limits; `_call_embedding_api` retries on failure but logs a warning and continues with empty embedding on repeated failure.
- `_is_indexable` uses `fnmatch` patterns (e.g., `*.py`, `*.js`) to filter files; it is called on every file in `run` and `status` – non-matching files are silently skipped, not indexed.
- CLI commands (`init`, `run`, `status`, `hook`) all require a valid git repository and call `is_git_repo()` early; they exit with error if not in a git repo.
- `_ensure_cache_gitignore` writes a `.gitignore` into `.cache/` only if one doesn't already contain `*` – it checks each line, so manual edits to that file are preserved.
- Cross-reference mapping (`cross_reference`) uses symbol IDs split by `::` to build caller→callee relationships; symbols without a delimiter (e.g., builtins) are ignored in the graph.
**root**
- TaskStore.update on a nonexistent task_id is a silent noop (no error, no side effect).
- TaskStore.get on a nonexistent task_id returns None, never raises KeyError or similar.
- RepoRegistry.get on a nonexistent relative path returns None immediately, not exception or empty list.
- _parse_body always returns a dict; returns {} if JSON decode fails or decoded value is not a dict.
- Config._apply_env treats empty string ('') as 'not set' and does NOT override the default value.
- Manifest file missing 'component_ids' or 'hash' keys loads as empty list/string, not error; corrupted manifest returns empty dict.

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