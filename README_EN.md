# repo-wiki

**Give code agents one verifiable view of a repository.**

repo-wiki builds a structural index from immutable Git trees, combines exact symbol lookup, SQLite FTS5, call-graph expansion, and optional dense enrichment, then projects Wiki pages and an Agent skill. CLI, REST, and MCP all use the same `RepositoryIndex` module and return results from the same generation.

[中文](README.md)

## Architecture

```text
Git tree / staged / worktree snapshot
                 │
                 ▼
content-addressed parse artifacts
                 │
                 ▼
SQLite generation + branch head ──► Wiki / Skill projection
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      Exact     FTS5    Call graph
        └────────┼────────┘
                 ▼
            ranked matches
                 │
          optional embedding revision
```

Core invariants:

- Inputs are Git trees, not mutable checkouts. `@staged` and `@worktree` are materialized as deterministic trees.
- A branch head moves only after a complete transaction commits; parse or store failures preserve the last visible generation.
- Parse artifacts and embeddings are content-addressed and reusable across branches.
- Local retrieval always works. `preferred` degrades on dense failure; `required` reports an explicit error.
- Each branch retains its two newest generations; unreachable generations, parse artifacts, and embeddings are collected automatically.

Runtime state lives in `.indexer/state/repository-index.sqlite3` with SQLite WAL, foreign keys, and FTS5. Synthetic staged/worktree objects live in `.indexer/state/git-objects` and never modify `.git`. Commit-friendly projections live in `wiki/` and `.indexer/skills/codebase.md`.

## Install

Python 3.11+ and Git are required.

```bash
pip install repo-wiki
```

From source:

```bash
git clone https://github.com/xzf475/repo-wiki.git
cd repo-wiki
pip install -e .
```

## Docker

Docker Compose starts the REST API and web console by default. The HTTP MCP service is optional. Create the local environment file before the first start:

```bash
cp .env.example .env
# Structural indexing and local retrieval do not require an embedding API key.
# Configure the provider key in .env only when dense enrichment is needed.

docker compose up -d --build
docker compose ps
curl --fail http://localhost:7654/health
```

After startup:

- Web console and REST API: <http://localhost:7654>
- Health check: <http://localhost:7654/health>
- MCP: disabled by default; set `MCP_ENABLED=true` in `.env` to listen on port `8000`

Main Docker environment variables:

| Variable | Default | Purpose |
|---|---:|---|
| `API_PORT` | `7654` | REST API and web console port |
| `REPO_WIKI_API_KEY` | empty | REST Bearer authentication; disabled when empty |
| `MCP_ENABLED` | `false` | Start the streamable HTTP MCP server alongside REST |
| `MCP_PORT` | `8000` | MCP listening port |
| `MCP_API_KEY` | empty | MCP Bearer authentication |
| `PUBLIC_DOMAIN` | empty | Public base URL used to generate webhook URLs |
| `WEBHOOK_SECRET` | empty | GitHub/GitLab webhook signature verification |
| `EMBEDDING_*` | see `.env.example` | Optional dense-enrichment provider settings |

Compose persists container data in named volumes:

| Volume | Container path | Contents |
|---|---|---|
| `repo_wiki_repos` | `/tmp/repo_wiki_repos` | Managed repositories, registry, per-repository indexes, and Wiki projections |
| `repo_wiki_data` | `/app/.indexer` | Index state under the service working directory |
| `repo_wiki_wiki` | `/app/wiki` | Wiki projections under the service working directory |

Common operations:

```bash
docker compose logs -f repo-wiki
docker compose restart repo-wiki
docker compose up -d --build     # rebuild after source or image changes
docker compose down              # stop containers and retain named volumes
```

`docker compose down -v` deletes the named volumes, including managed repositories and index data. Use it only when you intentionally want to clear all persisted data.

## CLI

```bash
repo-wiki init
repo-wiki run                 # structural generation + projections
repo-wiki run --enrich        # publish dense enrichment after the structural generation
repo-wiki run --staged
repo-wiki status
repo-wiki maintain            # recover jobs, collect state, verify SQLite
```

The pre-commit hook installed by `repo-wiki init` runs `repo-wiki run --staged`. It publishes one complete structural generation for the staged tree without calling a remote provider.

Agent helpers:

```bash
repo-wiki agent capabilities
repo-wiki agent schema
repo-wiki agent diagnose
repo-wiki agent context --symbol-id src/auth.py::validate_token
repo-wiki agent plan --goal "fix token validation" --symbol-id src/auth.py::validate_token
repo-wiki agent verify
```

## REST

```bash
repo-wiki serve-api --port 7654
```

Register and structurally index a repository:

```bash
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://github.com/org/repo.git","branch":"main","enrich":false}'
```

Search:

```bash
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"authentication middleware","repo":"repo","branch":"main","top_k":10,"retrieval":"preferred"}'
```

Multi-branch repositories require an explicit `branch`. Search responses include `generation`, `tree_id`, `retrieval`, and `degradations`; direct hits are in `matches`, graph expansion is in `related`.

Main repository endpoints:

| Path | Method | Purpose |
|---|---|---|
| `/register` | POST | Clone, register, and synchronize a repository |
| `/unregister` | POST | Remove registry metadata without deleting repository files |
| `/sync` | POST | Synchronize one branch; a new branch is registered automatically |
| `/sync-all` | POST | Synchronize every branch without checkout switching |
| `/search` | POST | Exact + FTS5 + Graph, with optional dense retrieval |
| `/trace` | POST | Upstream or downstream call graph |
| `/index-status` | POST | Generation, tree, and freshness |
| `/api/validate/{name}` | GET | Projection, generation, and SQLite integrity checks |
| `/repos` | GET | Registered repositories and branch generations |
| `/health` | GET | Service health |

See [API Reference](docs/api-reference.md) and [Agent Integration](docs/agent-integration.md) for full request contracts. The web console is served at `/`.

## MCP

Single-repository stdio mode:

```bash
cd /path/to/repo
repo-wiki serve
```

Multi-repository mode through REST:

```bash
repo-wiki serve --api http://localhost:7654
```

Core tools include `search_symbols_tool`, `trace_call_tool`, `get_source_context_tool`, `resolve_symbol_tool`, `impact_analysis_tool`, `change_plan_tool`, and `get_index_status_tool`. Search supports `local`, `preferred`, and `required` retrieval.

## Configuration

`.indexer.toml`:

```toml
[indexer]
wiki_dir = "wiki"
merge_threshold = 2

[hooks]
pre_commit = true

[embedding]
provider = "text-embedding-3-small"
api_key_env = "OPENAI_API_KEY"
base_url = ""
dimensions = 1536
```

Embedding is optional enrichment. Without a configured or available provider, structural generations, Wiki projection, and Exact/FTS5/Graph retrieval remain available.

Set `REPO_WIKI_API_KEY` for REST Bearer authentication and `WEBHOOK_SECRET` for webhook signature verification.

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, plus a generic text fallback parser.

## Verification

```bash
python -m pytest -q
python -m indexer.repository_benchmarks
```

The current quality and performance baseline is recorded in [docs/plans/2026-08-20-repository-index-baseline.json](docs/plans/2026-08-20-repository-index-baseline.json).

## License

MIT
