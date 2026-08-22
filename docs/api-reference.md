# repo-wiki API Reference

The REST adapter exposes the same published repository generations used by CLI and MCP. Start it with:

```bash
repo-wiki serve-api --host 0.0.0.0 --port 7654
```

All JSON write requests use `Content-Type: application/json`. If `REPO_WIKI_API_KEY` is set, send `Authorization: Bearer <key>`.

## Repository lifecycle

### `POST /register`

Clone, register, synchronize, and project a repository asynchronously.

```json
{
  "url": "https://github.com/org/backend.git",
  "name": "backend",
  "branch": "main",
  "branch_rule": "release/*",
  "description": "Order backend",
  "tags": ["orders", "go"],
  "token": "optional-secret",
  "enrich": false
}
```

`url` is required. `enrich` must be a boolean and defaults to `false`. Existing registrations return `409`; update them through sync endpoints. Credentials are sanitized from errors and are never returned.

Response:

```json
{
  "task_id": "...",
  "name": "backend",
  "status": "pending",
  "branches": ["main"]
}
```

### `POST /sync`

Synchronize one branch from an immutable Git ref. A branch not yet registered is appended to the repository registration.

```json
{"name":"backend","branch":"main","enrich":false}
```

### `POST /sync-all`

Fetch refs once, then synchronize all registered branches without switching the checkout.

```json
{"name":"backend","enrich":false}
```

The configured first branch is projected to `wiki/` and `.indexer/skills/codebase.md`; every branch retains its own generation and search scope. All branch scopes share content-addressed artifacts and snapshot overlays in one SQLite database. After successful branch syncs, scopes no longer present in the active Branch Rule are removed and orphaned storage is reclaimed. The asynchronous task result includes `removed_branches` and `storage_reclamation` counters.

### `POST /api/repo/{name}/sync`

Atomically update repository metadata and synchronize all branches.

```json
{
  "description": "Updated description",
  "tags": ["orders", "payments"],
  "branch_rule": "release/*",
  "enrich": false
}
```

### `POST /unregister`

```json
{"name":"backend"}
```

Removes registry metadata only. Repository files, the SQLite index, and projections are preserved.

### `GET /api/task/{task_id}`

Returns asynchronous task status, progress, step, errors, and the final result.

## Retrieval

### `POST /search`

```json
{
  "query": "validate JWT token",
  "repo": "backend",
  "branch": "main",
  "top_k": 10,
  "expand_depth": 1,
  "retrieval": "preferred"
}
```

Fields:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `query` | string | yes | Symbol ID, path, name, or natural-language query |
| `repo` | string | no | Limit to one registered repository |
| `branch` | string | conditionally | Required when a selected repository has multiple branches |
| `top_k` | integer | no | Direct match limit, 1–100 |
| `expand_depth` | integer | no | Call-graph expansion depth, 0–5 |
| `retrieval` | enum | no | `local`, `preferred`, or `required` |

`local` uses Exact + FTS5 + Graph. `preferred` adds dense candidates when a complete enrichment revision exists and degrades to local otherwise. `required` fails if dense retrieval cannot be completed.

Response shape:

```json
{
  "matches": [{"id":"auth.py::validate_token","repo":"backend","metadata":{"branch":"main"}}],
  "related": [],
  "total": 1,
  "search_metrics": [{
    "repo": "backend",
    "branch": "main",
    "generation": 4,
    "tree_id": "...",
    "retrieval": "local",
    "degradations": ["dense_not_ready"]
  }]
}
```

`matches` are ranked query hits. `related` contains graph expansion and is never mixed into the direct ranking.

### `POST /trace`

```json
{
  "symbol_id": "auth.py::validate_token",
  "repo": "backend",
  "branch": "main",
  "direction": "up",
  "max_depth": 3
}
```

`direction` is `up` for callers or `down` for callees. Multi-branch repositories require `branch`.

### `POST /source`

```json
{"repo":"backend","file":"auth.py","line_start":10,"line_end":40,"padding":5}
```

Returns bounded source context. Paths are validated against the repository root.

## Status and projections

| Path | Method | Result |
|---|---|---|
| `/repos` | GET | Registered repositories, branches, generations, trees, dense readiness |
| `/api/repo/{name}` | GET | Repository metadata, branch generation details, Wiki page list |
| `/api/repo/{name}/wiki/{page}` | GET | One generated Wiki page |
| `/api/validate/{name}` | GET | Config/projection presence, branch freshness, SQLite integrity |
| `/index-status` | POST | Generation, indexed/current tree, stale and removed files |
| `/health` | GET | REST process health |
| `/skill` | GET | Combined multi-repository Agent skill |

Validation health does not require dense enrichment. It requires a valid SQLite database, published branch generations, current structural state, and generated Wiki/skill projections.

## Agent endpoints

These endpoints derive results from the same generation-aware retrieval facade:

| Path | Purpose |
|---|---|
| `/edit-context` | Exact symbol context for editing |
| `/resolve-symbol` | Resolve an ambiguous symbol query |
| `/tests-for-symbol` | Locate candidate tests |
| `/pre-edit-check` | Preconditions and impact before editing |
| `/impact-analysis` | Upstream/downstream impact |
| `/change-plan` | Generate a repository-aware change plan |
| `/diagnose-index` | Diagnose generation, projection, and freshness state |
| `/agent-protocol` | Bundle context for a coding-agent protocol |
| `/locate-from-error` | Locate symbols from error text |
| `/entry-points` | List discovered entry points |
| `/post-edit-verify` | Suggest verification from a diff |
| `/change-set` | Build a scoped change set |
| `/coverage-map` | Map symbols to test coverage candidates |
| `/index-diff-report` | Compare symbol snapshots |
| `/cross-repo-graph` | Aggregate relations across repositories |
| `/stable-symbol-id` | Normalize a component ID |
| `/agent-capabilities` | Machine-readable tool catalog |
| `/agent-schema` | JSON/OpenAPI-style contracts |

## Component IDs

Component IDs are stable within a repository tree:

```text
relative/path.py::ClassName.method_name
relative/path.go::FunctionName
```

Always pair a component ID with repository and branch scope in multi-repository clients.

## Errors

Errors are JSON objects with an `error` message. Index failures use stable categories internally, including `SOURCE_UNAVAILABLE`, `PARSE_FAILED`, `SYNC_CONFLICT`, `STORE_BUSY`, `STORE_CORRUPT`, `INDEX_NOT_FOUND`, `ENRICHMENT_FAILED`, and `HYBRID_REQUIRED_UNAVAILABLE`.
