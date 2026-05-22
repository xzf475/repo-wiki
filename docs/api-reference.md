# repo-wiki API Reference

## Overview

repo-wiki REST API provides remote semantic code search across multiple repositories. It supports three usage modes:

1. **Pre-register local repos** — register already-indexed repos on server startup
2. **Register remote repos** — clone, index, and register repos via API
3. **MCP protocol** — for AI agents (Claude Code, Cursor, Windsurf)

## Quick Start

```bash
# Start the API server
repo-wiki serve-api --repos-dir /data/repos --port 8765

# Or with pre-registered local repos
repo-wiki serve-api --repo backend=/path/to/backend --repo frontend=/path/to/frontend --port 8765

# Auto-detect repos in current directory
repo-wiki serve-api --auto-detect --repos-dir /data/repos
```

## Base URL

```
http://{host}:{port}
```

Default: `http://0.0.0.0:8765`

---

## Endpoints

### POST /register

Clone a remote repository, index it, and register it for search.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Git repository URL (HTTPS) |
| `name` | string | No | Custom repo name. Auto-detected from URL if omitted |
| `username` | string | No | Username for private repos |
| `password` | string | No | Password for private repos |
| `token` | string | No | Personal access token (GitHub PAT, GitLab token, etc.) |
| `branch` | string | No | Branch to checkout. Default: repo's default branch |
| `skip_deep` | bool | No | Skip deep enrichment (narrative, flows, constraints). Default: `true` |
| `force_reindex` | bool | No | Force re-index if repo already registered. Default: `false` |

**Authentication Priority:** `token` > `username+password` > no auth

Credential handling:
- Credentials are injected into the URL for clone/pull operations
- After clone, credentials are stored in git credential helper (not in the URL)
- This enables automatic updates on subsequent pull/fetch operations

**Examples:**

```bash
# Public repo (no auth)
curl -X POST http://localhost:8765/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/org/public-repo.git"}'

# GitHub with Personal Access Token
curl -X POST http://localhost:8765/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/org/private-repo.git", "token": "ghp_xxxxxxxxxxxx"}'

# GitLab with username + password
curl -X POST http://localhost:8765/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://gitlab.com/team/api.git", "username": "myuser", "password": "mypass"}'

# Specify branch and custom name
curl -X POST http://localhost:8765/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/org/frontend.git", "name": "web-app", "branch": "develop"}'

# Force re-index an existing repo
curl -X POST http://localhost:8765/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/org/backend.git", "force_reindex": true, "skip_deep": false}'
```

**Response (200):**

```json
{
  "name": "backend",
  "path": "/data/repos/backend",
  "url": "https://github.com/org/backend.git",
  "has_vector_db": true,
  "symbol_count": 142,
  "indexed": true
}
```

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 400 | `url` field is missing |
| 409 | Repo already registered (use `force_reindex: true` to override) |
| 500 | git clone failed, git pull timed out, or indexing failed |

Error messages are sanitized — credentials (token, username, password) and the original URL are replaced with `<REDACTED_xxx>` markers.

---

### POST /unregister

Remove a repo from the registry (does not delete the cloned files).

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Repo name to unregister |

**Example:**

```bash
curl -X POST http://localhost:8765/unregister \
  -H "Content-Type: application/json" \
  -d '{"name": "backend"}'
```

**Response (200):**

```json
{
  "name": "backend",
  "unregistered": true
}
```

---

### POST /search

Semantic symbol search across registered repos.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `repo` | string | No | Limit search to a specific repo. Search all repos if omitted |
| `top_k` | int | No | Number of results per repo. Default: `10` |
| `expand_depth` | int | No | Call graph expansion depth (0=no expansion, 1=direct callers/callees). Default: `1` |

**Examples:**

```bash
# Search across all repos
curl -X POST http://localhost:8765/search \
  -H "Content-Type: application/json" \
  -d '{"query": "JWT token validation error"}'

# Search in a specific repo
curl -X POST http://localhost:8765/search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication middleware", "repo": "backend", "top_k": 5}'

# Search without call graph expansion (faster)
curl -X POST http://localhost:8765/search \
  -H "Content-Type: application/json" \
  -d '{"query": "database connection pool", "expand_depth": 0}'
```

**Response (200):**

```json
{
  "results": [
    {
      "id": "auth/token.py::TokenValidator.validate",
      "document": "[method] auth/token.py::TokenValidator.validate | Validates JWT tokens...",
      "metadata": {
        "type": "method",
        "file": "auth/token.py",
        "line_start": 45,
        "line_end": 67,
        "calls": "[\"decode\",\"fetch_keys\"]",
        "called_by": "[\"require_auth\"]",
        "imports": "[\"jwt\",\"requests\"]"
      },
      "distance": 0.231,
      "repo": "backend"
    }
  ],
  "total": 5
}
```

The `distance` field is cosine distance (lower = more relevant).

---

### POST /trace

Trace the call graph from a symbol, following calls downstream or callers upstream.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol_id` | string | Yes | Component ID (e.g. `auth/token.py::TokenValidator.validate`) |
| `direction` | string | No | `"down"` (follow calls) or `"up"` (follow callers). Default: `"down"` |
| `max_depth` | int | No | Maximum hops. Default: `3` |
| `repo` | string | No | Limit trace to a specific repo |

**Examples:**

```bash
# Trace downstream — what does this function call?
curl -X POST http://localhost:8765/trace \
  -H "Content-Type: application/json" \
  -d '{"symbol_id": "auth/token.py::TokenValidator.validate", "direction": "down"}'

# Trace upstream — who calls this function?
curl -X POST http://localhost:8765/trace \
  -H "Content-Type: application/json" \
  -d '{"symbol_id": "auth/token.py::TokenValidator.validate", "direction": "up", "max_depth": 5}'

# Trace in a specific repo
curl -X POST http://localhost:8765/trace \
  -H "Content-Type: application/json" \
  -d '{"symbol_id": "auth.py::require_auth", "direction": "up", "repo": "backend"}'
```

**Response (200):**

```json
{
  "results": [
    {
      "id": "auth/token.py::TokenValidator.validate",
      "document": "[method] Validates JWT tokens using JWKS public keys",
      "metadata": {
        "type": "method",
        "file": "auth/token.py",
        "line_start": 45,
        "line_end": 67
      },
      "repo": "backend"
    },
    {
      "id": "auth/token.py::TokenValidator.fetch_keys",
      "document": "[method] Fetches JWKS public keys from Auth0",
      "metadata": {
        "type": "method",
        "file": "auth/token.py",
        "line_start": 68,
        "line_end": 82
      },
      "repo": "backend"
    }
  ],
  "total": 2
}
```

---

### POST /source

Read source code around specific lines with line numbers.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | Yes | Repo-relative file path |
| `line_start` | int | Yes | Start line number |
| `line_end` | int | Yes | End line number |
| `repo` | string | Yes | Repo name |
| `padding` | int | No | Extra lines before/after the range. Default: `5` |

**Example:**

```bash
curl -X POST http://localhost:8765/source \
  -H "Content-Type: application/json" \
  -d '{"file_path": "auth/token.py", "line_start": 45, "line_end": 67, "repo": "backend"}'
```

**Response (200):**

```json
{
  "file_path": "auth/token.py",
  "repo": "backend",
  "line_start": 45,
  "line_end": 67,
  "source": "   40 | class TokenValidator:\n   41 |     \"\"\"Validates JWT tokens using JWKS.\"\"\"\n   42 | \n   45 |     def validate(self, token: str) -> UserClaims:\n   46 |         keys = self.fetch_keys()\n   47 |         decoded = jwt.decode(token, keys, algorithms=[\"RS256\"])\n   48 |         return UserClaims(**decoded)\n   49 |     \n   50 |     def fetch_keys(self) -> dict:\n   51 |         resp = requests.get(JWKS_URL)\n   52 |         return resp.json()[\"keys\"]\n   53 | ",
  "total_lines": 120
}
```

---

### POST /edit-context

Return an edit-ready context bundle for a symbol. This is the preferred endpoint before an Agent modifies code.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol_id` | string | Yes | Component ID to edit |
| `repo` | string | Required when multiple repos are registered | Repository name |
| `padding` | int | No | Source padding lines. Default: `8`, max `50` |

**Response (200):**

```json
{
  "repo": "backend",
  "symbol": {"id": "auth/token.py::TokenValidator.validate"},
  "source": "  45 | def validate(...):",
  "callers": [],
  "callees": [],
  "siblings": [],
  "candidate_tests": [],
  "index_status": {
    "is_stale": false,
    "indexed_commit": "abc123",
    "current_commit": "abc123"
  }
}
```

---

### POST /resolve-symbol

Resolve a query, symbol name, and optional hints into a concrete `component_id`.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Natural language query or symbol name |
| `repo` | string | Required when multiple repos are registered | Repository name |
| `file_hint` | string | No | File/path fragment to bias ranking |
| `type_hint` | string | No | Symbol type, such as `function`, `method`, or `class` |
| `top_k` | int | No | Candidate count. Default: `10`, max `50` |

Response `status` is `resolved`, `ambiguous`, or `not_found`.

---

### POST /tests-for-symbol

Find likely test files for a symbol using indexed files, naming conventions, imports, and symbol-name matches.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol_id` | string | Yes | Component ID |
| `repo` | string | No | Limit search to a specific repo |
| `max_results` | int | No | Maximum matches. Default: `10`, max `50` |

---

### POST /pre-edit-check

Run pre-edit checks for a symbol before an Agent modifies code.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol_id` | string | Yes | Component ID |
| `repo` | string | Required when multiple repos are registered | Repository name |

The response includes index freshness, dirty files, candidate tests, recommended test commands, callers, and callees.

---

### POST /impact-analysis

Analyze the likely impact of changing a symbol.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol_id` | string | Yes | Component ID |
| `repo` | string | Required when multiple repos are registered | Repository name |
| `max_depth` | int | No | Transitive call depth. Default: `2`, max `5` |

The response includes direct/indirect callers and callees, likely entry points, candidate tests, affected files, risk points, and index freshness.

---

### POST /change-plan

Generate an Agent-ready edit plan for a goal and target symbol.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal` | string | Yes | What the Agent needs to change |
| `symbol_id` | string | Yes | Target component ID |
| `repo` | string | Required when multiple repos are registered | Repository name |

The response includes files to read, edit targets, verification commands, candidate tests, risk points, and ordered steps.

---

### POST /diagnose-index

Diagnose whether an index is structurally usable.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo` | string | No | Limit diagnosis to a specific repo |

The response checks manifest presence, wiki index, skill file, vector DB, missing source files, missing wiki pages, freshness, and consistency ratios. `summary` includes manifest file count, missing source/wiki counts, stale/removed file counts, and artifact presence.

---

### POST /agent-protocol

Return compact fields optimized for Codex/Claude-style Agents.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal` | string | Yes | What the Agent needs to change |
| `symbol_id` | string | Yes | Target component ID |
| `repo` | string | Required when multiple repos are registered | Repository name |
| `protocol` | string | No | Output protocol label, such as `codex` or `claude` |

The response includes `read_these_files`, `edit_targets`, `verify_commands`, `warnings`, and `index_freshness` in a compact schema.

---

### POST /locate-from-error

Locate likely code symbols from stack traces, error logs, HTTP paths, or exception text.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error_text` | string | Yes | Stack trace, log line, HTTP error, or exception text |
| `repo` | string | No | Limit lookup to a specific repo |
| `top_k` | int | No | Candidate count. Default: `10`, max `50` |

The response includes parsed stack frames, HTTP paths, extracted terms, ranked candidates, match reasons, and index freshness.

---

### POST /entry-points

List first-class entry points discovered in indexed metadata.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo` | string | No | Limit lookup to a specific repo |
| `kind` | string | No | Optional kind filter: `api`, `cli`, `event`, `job`, or `webhook` |
| `max_results` | int | No | Maximum results. Default: `50`, max `200` |

The response includes entry point component IDs, kind, file, line range, document text, and index freshness.

---

### POST /post-edit-verify

Generate pre-commit verification guidance from edited files.

Local MCP mode reads `git diff` automatically when `diff` is omitted. Remote API/MCP mode should pass the local diff payload, because the remote server cannot see uncommitted local edits.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo` | string | Required when multiple repos are registered | Repository name |
| `diff` | string | No | Local `git diff` text. Required for remote callers that need local uncommitted changes analyzed |
| `changed_files` | string[] | No | Optional changed file list when diff is unavailable |

The response includes changed files, changed symbols, candidate tests, recommended verification commands, risk points, index freshness, whether reindexing is needed, and a checklist.

Diff payloads are capped by `REPO_WIKI_MAX_DIFF_BYTES` (default 2 MiB). Oversized diffs return HTTP 413.

---

### POST /change-set

Build the must-change set for an Agent task.

Remote callers should pass `diff` when the change is still local and uncommitted.

**Request Body:** `repo`, `goal`, optional `symbol_id`, optional `diff`, optional `changed_files`, optional `max_results`, optional `include_details`.

Returns target symbols, files that should be considered together, related symbols, candidate tests, verification commands, risks, and freshness.

Large responses are capped by `max_results`. Set `include_details=false` for summary-first Agent handoffs.

---

### POST /coverage-map

Map source symbols to likely covering tests.

**Request Body:** `repo`, optional `symbol_id`.

When `symbol_id` is provided, returns whether that symbol appears covered and the likely tests. Without `symbol_id`, returns a repo-wide symbol coverage map.

---

### POST /index-diff-report

Compare two index snapshots.

**Request Body:** `repo`, `before_nodes`, `after_nodes`.

Returns added/removed/changed symbols, rename/move matches via stable IDs, entry point changes, and call graph edge changes.

---

### POST /cross-repo-graph

Build a cross-repo dependency graph across registered repos.

**Request Body:** optional `repos` list.

Returns edges such as frontend API client symbols pointing to backend route symbols through shared HTTP paths. GraphQL operation names are also linked when the same operation appears in client and server symbols.

---

### POST /stable-symbol-id

Generate a deterministic stable symbol ID.

**Request Body:** `symbol_id`, optional `symbol_type`, optional `file_path`, optional `source`.

The stable ID is also stored in vector metadata for newly indexed symbols. `index-diff-report` uses stable IDs to report rename/move events instead of treating them only as delete+add.

---

### GET /agent-capabilities

Return the Agent-facing tool manifest and recommended local/remote flow. Each tool entry includes modes, JSON input schema, output schema, example input, and recommended next tools. The response also embeds `json_schema` for validating the manifest itself.

---

### GET /agent-schema

Return an OpenAPI 3.1 document for Agent-facing endpoints.

The schema includes request examples and response schemas for `/search`, `/resolve-symbol`, `/impact-analysis`, `/change-plan`, `/post-edit-verify`, `/change-set`, `/coverage-map`, `/index-diff-report`, `/cross-repo-graph`, and `/agent-capabilities`.

---

### POST /index-status

Report whether registered indexes are stale relative to the current workspace.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo` | string | No | Limit status to a specific repo |

The response includes `is_stale`, `reasons`, indexed/current commits, stale files, removed files, and counts.

---

### GET /repos

List all registered repos and their status.

**Example:**

```bash
curl http://localhost:8765/repos
```

**Response (200):**

```json
{
  "repos": [
    {
      "name": "backend",
      "path": "/data/repos/backend",
      "has_vector_db": true,
      "symbol_count": 142
    },
    {
      "name": "frontend",
      "path": "/data/repos/frontend",
      "has_vector_db": true,
      "symbol_count": 87
    }
  ]
}
```

---

### GET /health

Health check endpoint.

**Example:**

```bash
curl http://localhost:8765/health
```

**Response (200):**

```json
{
  "status": "ok",
  "repos": 2
}
```

---

## BUG Analysis Workflow

The typical flow for automated bug analysis and fix:

```
1. POST /register   →  Bind the relevant repo(s)
2. POST /search     →  Find symbols related to the bug description
3. POST /trace      →  Trace the call chain (upstream = who triggers the bug, downstream = what it affects)
4. POST /source     →  Read the exact code at the bug location
5. Apply fix        →  Your automated fix pipeline reads the source and generates a patch
```

**Example: Bug "Auth0 JWT validation fails with expired tokens"**

```bash
# Step 1: Register repos (if not already done)
curl -X POST http://localhost:8765/register \
  -d '{"url": "https://github.com/org/backend.git", "token": "ghp_xxx"}'

# Step 2: Search for relevant symbols
curl -X POST http://localhost:8765/search \
  -d '{"query": "JWT token validation expired error", "top_k": 5}'

# Step 3: Trace upstream — who triggers this code?
curl -X POST http://localhost:8765/trace \
  -d '{"symbol_id": "auth/token.py::TokenValidator.validate", "direction": "up", "max_depth": 4}'

# Step 4: Read the exact code
curl -X POST http://localhost:8765/source \
  -d '{"file_path": "auth/token.py", "line_start": 45, "line_end": 67, "repo": "backend"}'

# Step 5: AI generates fix based on the code context
```

---

## Component ID Format

Symbol identifiers follow this pattern:

```
relative/path.py::ClassName.method_name    ← method
relative/path.py::ClassName                ← class
relative/path.py::function_name            ← top-level function
```

For JS/TS files:

```
src/auth/tokenValidator.ts::TokenValidator.validate
src/utils/helpers.ts::formatDate
```

---

## Configuration

The API server reads per-repo `.indexer.toml` config files. Global defaults:

```toml
[embedding]
provider = "dashscope/text-embedding-v4"
api_key_env = "DASHSCOPE_API_KEY"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
dimensions = 1024

[vector_store]
backend = "chromadb"
persist_dir = ".indexer/vector_db"
collection_name = "repo-wiki_code"
```

Environment variables required:
- `DASHSCOPE_API_KEY` — for embedding generation (百炼平台)
- `ANTHROPIC_API_KEY` or equivalent — for LLM descriptions (only during indexing)
