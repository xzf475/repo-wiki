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

- **66 symbols** across **1 files** — indexed 2026-05-06 @ `fe25e877`
- Wiki: `wiki/` — 1 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a REST API for managing and indexing code repositories, implemented in `indexer/rest_api.py`. It uses `RepoRegistry` to persist repository metadata and `TaskStore` to manage indexing tasks via an asynchronous task queue. Endpoints like `register_repo`, `sync_repo`, and `reindex_repo` trigger task creation and orchestrate repository validation, syncing, and rebuilding. Middleware classes `_LoggingMiddleware` and `_AuthMiddleware` provide request logging and JWT-based authentication for all API routes.
## Key Request Flows
- POST /repos → register_repo → RepoRegistry.register → _run_register_task → TaskStore.create
- POST /sync/{name} → sync_repo → RepoRegistry.get → _run_all → TaskStore.create (sync task)
- POST /reindex/{name} → reindex_repo → RepoRegistry.get → _run_all → TaskStore.create (reindex task)
- POST /webhook/{name} → webhook_by_name → _index_page → TaskStore.create (partial index)
- GET /health → health → RepoRegistry.list_names (liveness check)

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [root](../wiki/root.md) | indexer/rest_api.py | TaskStore.__init__, TaskStore._cleanup, TaskStore.create, TaskStore.get, TaskStore.update |
## Critical Constraints (read before editing)
**root**
- Concurrency per repo is strictly serialized: _get_repo_lock returns a threading.Lock local to the module, not shared across processes, so only one indexing task per repo can run inside a single worker.
- TaskStore._cleanup runs on every create() call (not on a timer), removing tasks older than a fixed expiry threshold; thus stale tasks are only purged coincident with new task creation.
- RepoRegistry persists as JSON to a temp directory (via gettempdir) under a subfolder '.indexify/registry'; the file is written atomically by writing to a temp suffix and then replacing the original.
- Branch pattern matching in _match_branch_rule uses Python's fnmatch on comma-separated globs, but each pattern is stripped; no support for negated patterns or regex.
- Default branch detection (_detect_default_branch) uses `git ls-remote --symref <url> HEAD` and parses the first line; relies on git being installed and network access at registration time.
- register_repo blocks the web thread for clone (via run_in_executor); synchronous file operations may cause timeouts if git clone is slow, but there is no explicit timeout exposed.

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