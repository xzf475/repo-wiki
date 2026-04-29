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

- **62 symbols** across **2 files** — indexed 2026-04-29 @ `d3851c5d`
- Wiki: `wiki/` — 1 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The indexer service manages repository registration and indexing tasks via a REST API (indexer/rest_api.py). Core components are the RepoRegistry (persistent repo metadata store) and TaskStore (asynchronous task queue for indexing operations). The service exposes endpoints for registering/unregistering repos, triggering sync/rebuild, and checking status, with authentication and logging middleware wrapping all requests.
## Key Request Flows
- register_repo endpoint → validate_repo → RepoRegistry.register → _run_register_task → TaskStore.create → async indexer task
- sync_repo endpoint → RepoRegistry.get → TaskStore.create (sync task) → _index_page → repo retrieval logic
- webhook_by_name endpoint → RepoRegistry.get → TaskStore.create (rebuild task) → rebuild_repo → _run_all
- health endpoint → TaskStore.get (status check) → return health status
- request → _AuthMiddleware.dispatch (JWT validation) → route handler → response → _LoggingMiddleware.dispatch

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/rest_api.py, indexer/retrieval.py | TaskStore, TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get |
## Critical Constraints (read before editing)
**indexer**
- A per-repo lock (via `_get_repo_lock`) prevents concurrent register/sync/rebuild operations on the same repo; the lock must be explicitly acquired and released in each task function.
- `TaskStore._cleanup` is called on every `create()`, removing stale tasks older than max age; callers must not rely on tasks persisting indefinitely.
- `RepoRegistry` stores data in a temporary directory (`gettempdir`), so registry is ephemeral across restarts unless persisted elsewhere.
- Default branch detection and remote branch listing use `git ls-remote`; they may fail or return empty for repositories without remotes or with authentication issues.
- Unregister (`unregister_repo`) only removes the entry from `RepoRegistry`; it does not delete indexed data or the local clone (that is left to a separate cleanup or subsequent rebuild).
- Validation computes tracked file counts from `all_tracked_files` and sums file counts from manifest; missing files are reported but not automatically fixed.

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