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