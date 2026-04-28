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

This skill uses the repo-wiki MCP server to provide semantic code understanding across registered repositories. It offers four tools that work together as a diagnostic pipeline.

## Tool Pipeline

```
list_repos → search_symbols_tool → trace_call_tool → get_source_context_tool
   (发现)        (定位符号)            (追踪关系)          (阅读源码)
```

### When to use each tool

| Phase | Tool | When |
|-------|------|------|
| 1. Scouting | `list_repos` | First thing — discover which repos exist |
| 2. Locating | `search_symbols_tool` | User asks about a feature, bug, error, or module |
| 3. Tracing | `trace_call_tool` | After finding a symbol — understand callers/callees |
| 4. Reading | `get_source_context_tool` | After finding a symbol or trace — read actual code |

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

## Common Workflows

### Workflow A: Bug Analysis
```
1. search_symbols_tool(query="<error message or bug description>")
   → Find suspicious symbols

2. trace_call_tool(symbol_id="<found symbol>", direction="up")
   → Find where the buggy code is called from (root cause)

3. get_source_context_tool(file_path="<file>", line_start=<line>, line_end=<line>)
   → Read actual code

4. trace_call_tool(symbol_id="<root cause>", direction="down")
   → Understand impact scope
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
