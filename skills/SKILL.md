---
name: repo-wiki-code-analysis
description: >
  Use repo-wiki MCP tools to semantically search, trace, and read source code
  across registered repositories. This skill is triggered when the user asks
  about understanding, debugging, tracing, or analyzing code — such as "find
  where X is implemented", "trace how this function is called", "show me the
  source around this error", "what does this module do", "debug this bug",
  "review this code path", or "find code related to an error message".
  Always invoke these tools BEFORE attempting to guess or synthesize code
  details the AI can't know. Prefer searching over guessing.
---

# repo-wiki Code Analysis

This skill uses the repo-wiki MCP server to provide semantic code understanding across registered repositories. It offers Agent-focused tools that work together as a diagnostic and edit-preparation pipeline.

## Tool Pipeline

```
list_repos → locate_from_error_tool/search_symbols_tool → resolve_symbol_tool → impact_analysis_tool → change_plan_tool
   (发现)        (错误/语义召回)                     (消歧定位)             (影响面)              (修改计划)
```

### When to use each tool

| Phase | Tool | When |
|-------|------|------|
| 1. Scouting | `list_repos` | First thing — discover which repos exist |
| 2. Locating | `search_symbols_tool` | User asks about a feature, bug, error, or module |
| 3. Resolving | `resolve_symbol_tool` | Convert query + hints to a concrete `component_id`; handle ambiguity before reading/editing |
| 4. Tracing | `trace_call_tool` | After finding a symbol — understand callers/callees |
| 5. Reading | `get_source_context_tool` | After finding a symbol or trace — read actual code |
| 6. Edit prep | `get_edit_context_tool` | Before modifying code — gather source, relationships, sibling symbols, tests, and freshness |
| 7. Pre-edit check | `pre_edit_check_tool` | Before modifying code — check index freshness, dirty files, impact, and recommended tests |
| 8. Verification | `find_tests_for_symbol_tool` | Before/after edits — identify likely tests |
| 9. Freshness | `get_index_status_tool` | When results seem stale or before high-risk edits |
| 10. Impact | `impact_analysis_tool` | Before edits — understand direct/transitive callers, callees, entry points, tests, and risk |
| 11. Planning | `change_plan_tool` | Before edits — produce files to read, edit targets, verification commands, and risks |
| 12. Diagnosis | `diagnose_index_tool` | When search results look wrong or index artifacts may be broken |
| 13. Agent protocol | `agent_protocol_tool` | When another Agent needs a compact handoff payload |
| 14. Error location | `locate_from_error_tool` | Start here when the user provides stack traces, logs, HTTP paths, or exception text |
| 15. Entry points | `list_entry_points_tool` | Find API routes, CLI commands, event handlers, jobs, and webhooks |
| 16. Post-edit verify | `post_edit_verify_tool` | After edits, before commit/push — map diff to symbols, tests, commands, risks |
| 17. Change set | `change_set_tool` | Before or after edits — find files/symbols/tests that must move together |
| 18. Coverage | `coverage_map_tool` | Check whether a source symbol has likely test coverage |
| 19. Index diff | `index_diff_report_tool` | Compare index snapshots after reindexing |
| 20. Cross repo | `cross_repo_graph_tool` | Find frontend/backend/SDK/service dependency edges |
| 21. Capabilities | `agent_capabilities_manifest_tool` | Discover available tools and recommended flow |

## Tool Reference

### 1. `list_repos` — Discover available repositories

Call this first when the user hasn't specified a repo. Shows repo names, symbol counts, last indexed commit, and whether vector DB exists.

**No parameters needed.**

**Example output:**
```
**bug_agent** @a1b2c3d — 2055 symbols, 120 files, has vector DB
```

### 2. `search_symbols_tool` — Semantic code search

Search code by meaning, not by keywords. Uses semantic embeddings to find relevant symbols even when the query uses different wording than the code.

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | yes | — | Natural language description (e.g. "JWT token validation", "database connection pool") |
| `repo` | string | no | all repos | Repository name to search in |
| `top_k` | int | no | 10 | Number of top results |
| `expand_depth` | int | no | 1 | Call graph expansion hops (0=none, 1=direct) |
| `rewrite` | bool | no | true | Use LLM query rewriting for better recall |

**Workflow:**
1. Start with a broad semantic query and `top_k=10`
2. If too many results, narrow with `repo` filter or more specific `query`
3. Set `expand_depth=1` to see direct callers/callees in search results
4. Set `rewrite=true` (default) to automatically expand short queries into better semantic matches

**Query writing guide:**
- Describe what the code *does*, not what it's *named*
- Good: `"user authentication with JWT tokens and session management"`
- Good: `"error handling for database connection timeouts"`
- Avoid: `"auth.go"` or `"connect function"` (these are names, not semantics)

**Example:**
```
User: "How does the error handling work in the auth module?"
→ search_symbols_tool(query="error handling for authentication", repo="bug_agent", top_k=5)
```

### 3. `trace_call_tool` — Call graph tracing

After finding a symbol via search, trace its relationships to understand how data flows and which code paths affect each other.

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol_id` | string | yes | — | Symbol ID in format `path/to/file.py::ClassName.method` or `path/to/file.py::function_name` |
| `repo` | string | yes | — | Repository name |
| `direction` | string | no | "down" | `"down"` (calls this symbol makes) or `"up"` (callers of this symbol) |
| `max_depth` | int | no | 3 | Maximum call graph hops |

**Tracing strategies:**
- **Bug diagnosis**: use `direction="up"` from the error location to find root cause
- **Impact analysis**: use `direction="down"` from a function to see what would break if you change it
- **Feature flow**: trace `direction="up"` from implementation to entry points, then `direction="down"` from entry point to understand full flow
- **Start shallow** (`max_depth=1`), then increase depth for deeper understanding

**Example:**
```
User: "What calls the login handler?"
→ trace_call_tool(symbol_id="server/auth/handler.go::LoginHandler", repo="bug_agent", direction="up")
```

### 4. `get_source_context_tool` — Read source code

After locating symbols via search or trace, read the actual source code with line numbers and context padding.

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file_path` | string | yes | — | Repo-relative file path (e.g. `"src/auth/token_validator.go"`) |
| `repo` | string | yes | — | Repository name |
| `line_start` | int | yes | — | Start line number |
| `line_end` | int | yes | — | End line number |
| `padding` | int | no | 5 | Extra lines before and after |

**Usage pattern:**
- Read 20-30 line chunks at a time for readability
- Use `padding=5` for context around a specific symbol
- Use `padding=0` for precise symbol-only read

**Example:**
```
User: "Show me the code around the JWT validation"
First find it: search_symbols_tool(query="JWT token validation")
Then read it:  get_source_context_tool(file_path="server/auth/token_validator.go", repo="bug_agent", line_start=42, line_end=68)
```

### 5. Agent edit-preparation tools

Use these after `resolve_symbol_tool` returns a concrete `component_id`.

| Tool | Use |
|------|-----|
| `impact_analysis_tool` | Find callers, callees, entry points, candidate tests, affected files, risks, and freshness |
| `change_plan_tool` | Turn a goal and symbol into `read_these_files`, `edit_targets`, `verify_commands`, and ordered steps |
| `diagnose_index_tool` | Check manifest/wiki/vector/source/freshness health when results are empty or suspicious |
| `agent_protocol_tool` | Produce compact Codex/Claude-style handoff fields |
| `locate_from_error_tool` | Turn stack traces, logs, and HTTP paths into ranked code candidates |
| `list_entry_points_tool` | List indexed API/CLI/event/job/webhook entry points |
| `post_edit_verify_tool` | Use after edits; local mode reads `git diff`, remote mode should pass `diff` explicitly |
| `change_set_tool` | Expand a goal/symbol/diff into must-change files, related symbols, tests, and commands |
| `coverage_map_tool` | Return likely tests for a source symbol and whether it appears covered |
| `index_diff_report_tool` | Report added/removed/changed symbols, entry point changes, and call graph changes |
| `cross_repo_graph_tool` | Build cross-repo HTTP path dependency edges |
| `stable_symbol_id_tool` | Generate stable IDs for rename/move tracking |
| `agent_capabilities_manifest_tool` | Return local/remote capability manifest |

## Common Workflows

### Workflow A: Bug Analysis
```
1. locate_from_error_tool(error_text="<stack trace, log, HTTP path, or exception>")
   → Find ranked code candidates from concrete runtime evidence

2. resolve_symbol_tool(query="<best candidate or user wording>")
   → Resolve to a concrete component ID

3. impact_analysis_tool(symbol_id="<resolved symbol>")
   → Find where the buggy code is called from (root cause)

4. get_source_context_tool(file_path="<file>", line_start=<line>, line_end=<line>)
   → Read actual code

5. change_plan_tool(goal="<fix goal>", symbol_id="<resolved symbol>")
   → Get read targets, edit target, verification commands, and risks

6. post_edit_verify_tool()
   → Before commit/push, verify changed symbols, tests, commands, risks, and reindex need

7. change_set_tool(goal="<fix goal>", diff="<optional diff>")
   → Confirm no related file/symbol/test is missing before commit
```

### Workflow B: Feature Understanding
```
1. search_symbols_tool(query="<feature description>")
   → Locate relevant implementation

2. get_source_context_tool(...) for each key symbol
   → Read implementation details

3. trace_call_tool(symbol_id="<entry point>", direction="down")
   → Understand full execution flow
```

### Workflow C: Code Review / PR Analysis
```
1. search_symbols_tool(query="<what the PR changes>")
   → Find affected symbols

2. trace_call_tool(symbol_id="<each changed symbol>", direction="up", depth=1)
   → Check all callers are updated

3. trace_call_tool(symbol_id="<each changed symbol>", direction="down")
   → Verify no downstream breakage
```

## Important Guidelines

- **Search before guessing.** If the user asks about code implementation details, always search first. Don't hallucinate code.
- **Use semantic queries.** Describe what the code does, not what files are named. The search is semantic, not keyword-based.
- **Iterate.** Start broad, then narrow. First search with a general query, then use the results to refine.
- **Read after finding.** Search results include symbol IDs. Always follow up with `get_source_context_tool` to read actual code before making claims.
- **Multi-repo support.** When no `repo` is specified, search crosses all registered repos. Use `repo` filter to narrow when results are too broad.
- **No repo found.** If `list_repos` returns empty, tell the user no repositories are registered and ask them to set up repo-wiki first.
