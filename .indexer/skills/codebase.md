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

- **62 symbols** across **2 files** — indexed 2026-04-29 @ `d388569d`
- Wiki: `wiki/` — 1 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

This indexer service manages code repository indexing and retrieval via a REST API. The core components are `TaskStore` for tracking background indexing tasks and `RepoRegistry` for persisting repository metadata, both used by endpoints in `indexer/rest_api.py`. The `indexer/retrieval.py` module (not detailed here) handles retrieval logic. The service supports registering, syncing, rebuilding, and unregistering repos, with middleware for logging (`_LoggingMiddleware`) and authentication (`_AuthMiddleware`).
## Key Request Flows
- Register repo endpoint → `register_repo` → `_run_register_task` → `TaskStore.create` → background indexing
- Sync repo endpoint → `sync_repo` → `TaskStore.update` as task starts → triggers indexing of branches
- Health check → `health` endpoint → returns basic service status (no TaskStore dependency)
- Unregister repo → `unregister_repo` → `RepoRegistry.unregister` → `RepoRegistry._save` to persist change
- List repos → `list_repos` → `RepoRegistry.list_names` → returns all registered repo names

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/rest_api.py, indexer/retrieval.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get |
## Critical Constraints (read before editing)
**indexer**
- Per-repo lock acquired via `_get_repo_lock` (a `Lock` per repo name); two operations on the same repo will be serialized, but different repos can run concurrently.
- `TaskStore` is purely in-memory and tasks expire after a hardcoded TTL (checked in `_cleanup`). Task IDs (UUIDs) are transient — lost on server restart.
- `RepoRegistry` stores entries on disk (temp directory) with a legacy migration path (`_load` converts old format and detects default branch via `_detect_default_branch`). Saving happens synchronously after every mutation.
- Remote branch discovery (`_discover_remote_branches`) uses `git ls-remote` with fnmatch glob patterns; results are cached only during the call — no persistent branch list.
- Default branch detection (`_detect_default_branch`) parses `git symbolic-ref` output; fallback is 'main' if detection fails (handled in `_load` via warning).
- Indexing pipeline functions (`describe_nodes`, `deep_enrich_pages`, `build_batches`, `density_group`) are expected to be synchronous and run inside `run_in_executor` to avoid blocking the event loop.

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