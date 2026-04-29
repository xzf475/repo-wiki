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

- **72 symbols** across **2 files** — indexed 2026-04-29 @ `e7850e36`
- Wiki: `wiki/` — 1 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## System Overview

The system is a code indexing service with dual interfaces: an MCP (Model Context Protocol) server exposing tools for symbol search, call tracing, and source context retrieval, and a REST API for repository management (register, sync, rebuild, unregister) and task tracking. Core components include the `indexer/mcp_server.py` serving MCP tools, `indexer/rest_api.py` hosting REST endpoints, `TaskStore` for asynchronous task creation and lifecycle, and `RepoRegistry` for persistent repository state. Middleware layers (`_MCPAuthMiddleware`, `_LoggingMiddleware`, `_AuthMiddleware`) provide authentication and logging across both interfaces, while a webhook endpoint (`webhook_by_name`) enables event-driven reindexing.
## Key Request Flows
- MCP client → _MCPAuthMiddleware.dispatch → search_symbols_tool (symbol lookup)
- REST client → _AuthMiddleware.dispatch → register_repo → TaskStore.create → _run_register_task → RepoRegistry.register
- REST client → sync_repo → TaskStore.create → (sync task targeting a repository)
- Webhook POST → webhook_by_name → validates event → triggers indexing tasks via TaskStore.create
- Any request → _LoggingMiddleware.dispatch → _AuthMiddleware.dispatch → route handler (REST or MCP)

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [indexer](../wiki/indexer.md) | indexer/mcp_server.py, indexer/rest_api.py | _patched_method, search_symbols_tool, trace_call_tool, get_source_context_tool, list_repos |
## Critical Constraints (read before editing)
**indexer**
- The MCP authentication patching (_apply_mcp_auth) is only applied when create_server is called directly; the REST API backend mode (create_api_server) has no auth layer.
- TaskStore entries older than 1 hour are silently removed on every create() call, so long-running tasks may expire before being polled.
- RepoRegistry persistence uses a single temp JSON file (no database); data is lost on machine reboot unless re-registered.
- Default branch detection (_detect_default_branch) requires network access to the remote git endpoint and may silently fail for unreachable repos.
- The context tool (get_source_context_tool) returns raw code lines without any sanitization; callers must handle potentially large output.
- The direct server mode (create_server) uses the current working directory (cwd) as the base path, making it sensitive to the process's startup directory.

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