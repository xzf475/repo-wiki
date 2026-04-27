# repo-wiki

**Your codebase, understood by any LLM.**

Generate a checked-in wiki, skill files, and vector search from any repo — no cloud, no lock-in.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![Forked from kiwiskil](https://img.shields.io/badge/forked%20from-kiwiskil-6366f1)](https://github.com/ximihoque/kiwiskil)

[中文文档](README.md)

---

repo-wiki generates a structural wiki, skill files, and a vector search index from any codebase. It enables LLM agents to navigate code without reading source files — using a knowledge graph built from your repo and checked into git.

> **Forked from [kiwiskil](https://github.com/ximihoque/kiwiskil)** — repo-wiki extends the original with a REST API, vector search, query rewriting, health checks, webhook auto-sync, MCP server, and Rust/Java/Ruby/Go support.

---

## Table of Contents

- [How It Works](#how-it-works)
- [What's Different from kiwiskil](#whats-different-from-kiwiskil)
- [Install](#install)
- [Quick Start](#quick-start)
- [CLI](#cli)
- [Output](#output)
- [REST API](#rest-api)
  - [Repository Management](#repository-management)
  - [Search & Navigation](#search--navigation)
  - [Webhook Auto-Sync](#webhook-auto-sync)
  - [Search with Query Rewriting](#search-with-query-rewriting)
  - [API Authentication](#api-authentication)
- [MCP Server](#mcp-server)
  - [Modes](#modes)
  - [Integration with LLM Clients](#integration-with-llm-clients)
  - [Loading the Skill](#loading-the-skill)
- [Configuration](#configuration)
  - [.indexer.toml](#indextoml-per-repo-created-by-repo-wiki-init)
  - [.env](#env-server-level-for-rest-api--mcp-mode)
- [Supported Languages](#supported-languages)
- [Design Principles](#design-principles)
- [License](#license)

---

## How It Works

1. **AST parsing** — extracts symbols, imports, and call graphs from source files (deterministic, free)
2. **LLM descriptions** — adds one-line descriptions per symbol via LiteLLM (any provider)
3. **Density-based grouping** — organizes files into wiki pages by logical density, not directory structure
4. **Embedding** — generates vector representations for every symbol
5. **ChromaDB** — stores and indexes vectors for fast semantic search
6. **Pre-commit hook** — keeps the wiki in sync on every commit
7. **Skill file** — generates `.indexer/skills/codebase.md` so any LLM agent can navigate your codebase

The wiki is plain markdown checked into your repo. No cloud service, no lock-in.

---

## What's Different from kiwiskil

| Feature | kiwiskil | repo-wiki |
|---------|----------|-----------|
| Structural wiki + skill file | ✓ | ✓ |
| Pre-commit hook | ✓ | ✓ |
| REST API with Web UI | — | ✓ |
| Vector search (ChromaDB) | — | ✓ |
| Query rewriting | — | ✓ |
| Call graph tracing | — | ✓ |
| Health checks | — | ✓ |
| Auto-repair on sync | — | ✓ |
| Webhook auto-sync | — | ✓ |
| MCP server | — | ✓ |
| Rust / Java / Ruby / Go | — | ✓ |
| Async task processing | — | ✓ |

---

## Install

```bash
pip install repo-wiki
```

---

## Quick Start

### CLI Mode (Single Repo)

```bash
# In any git repo
repo-wiki init       # creates .indexer.toml, installs pre-commit hook, appends CLAUDE.md
repo-wiki run        # generates wiki/ and .indexer/skills/codebase.md
```

On every subsequent commit, the pre-commit hook runs `repo-wiki run --staged` automatically — only changed files are re-indexed.

### REST API Mode (Multi-Repo)

```bash
# Start the API server
repo-wiki serve-api --port 7654

# Register a remote repo (clones + indexes)
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'
# Response includes a webhook_url ready to configure in GitHub

# Search across repos
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "authentication middleware", "top_k": 10}'

# Open the web dashboard
open http://localhost:7654
```

### Docker Deployment

```bash
# 1. Clone the project
git clone https://github.com/your/repo-wiki.git
cd repo-wiki

# 2. Configure environment variables
#    Copy .env.example to .env and fill in your API keys
cp .env.example .env
#    Edit .env, at minimum configure:
#     LLM_API_KEY_ENV=DASHSCOPE_API_KEY
#     DASHSCOPE_API_KEY=sk-xxx
#     EMBEDDING_API_KEY_ENV=DASHSCOPE_API_KEY

# 3. Build and start
docker compose up -d

# 4. Check logs to confirm startup
docker compose logs -f

# 5. Register a repo
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'

# 6. Stop
docker compose down
```

Place `.env` in the project root — `docker-compose.yml` mounts it into the container automatically. All index data is persisted in Docker volumes and survives container restarts. See the [Configuration](#env-server-level-for-rest-api--mcp-mode) section for details.

### MCP Mode (LLM Agent Integration)

```bash
# Single-repo mode — reads the local vector store directly
repo-wiki serve

# Multi-repo mode — connects to a REST API backend
repo-wiki serve --api http://localhost:7654
```

See the [MCP Server](#mcp-server) section for details.

---

## CLI

```bash
repo-wiki init               # set up config, hook, and CLAUDE.md
repo-wiki run                # smart incremental + deep enrichment (default)
repo-wiki run --skip-deep    # skip narrative/flows/constraints (faster)
repo-wiki run --force        # force full re-index
repo-wiki run --staged       # incremental on staged files only (hook)
repo-wiki status             # show last indexed commit, stale files, stats
repo-wiki hook install       # manually install pre-commit hook
repo-wiki hook remove        # remove pre-commit hook
repo-wiki serve              # start MCP server
repo-wiki serve-api          # start REST API server with web dashboard

# Docker
docker compose up -d         # build and start in background
docker compose logs -f       # follow logs
docker compose down          # stop and remove containers
```

### Deep Mode

By default, `repo-wiki run` performs a **deep enrichment** pass after structural indexing. This uses your configured LLM to generate:

- **System narrative** — a plain-English overview of what the codebase does
- **Key request flows** — end-to-end data flows across modules
- **Design constraints** — per-module gotchas, invariants, and non-obvious rules

These appear in `wiki/INDEX.md` and in the skill file, giving agents richer context without reading source. Use `--skip-deep` to run structural-only indexing when speed matters.

---

## Output

### `wiki/INDEX.md`

Top-level map of the entire codebase — which wiki page covers which files, entry points for each group, system overview, and key request flows (when deep mode is enabled).

### `wiki/<group>.md`

One page per logical folder cluster. Each page contains:

- **Modules** — files covered
- **Key Symbols** — functions, classes, methods with one-line descriptions
- **Relationships** — what this group calls, what calls it, what it imports
- **Entry Points** — symbols with no callers (architectural roots)
- **Data Flows** — end-to-end flows through this module *(deep mode)*
- **Design Constraints** — invariants and non-obvious rules to respect *(deep mode)*

### `.indexer/skills/codebase.md`

A skill file that teaches any LLM agent how to navigate your codebase:

- Codebase stats (symbol count, file count, index date, commit)
- System overview and key request flows
- Wiki page index with entry points
- Critical constraints extracted per module
- Step-by-step navigation workflow for agents
- Component ID format reference and manifest lookup instructions

### `.indexer/vector_db/`

ChromaDB vector store containing embeddings for every indexed symbol. Used by the REST API and MCP server for semantic search.

---

## REST API

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/repos` | GET | List all registered repos |
| `/register` | POST | Register & index a repo from URL. Accepts `branches` array or `branch` string, defaults to `["main"]` |
| `/sync` | POST | Sync a specific branch (git pull + incremental re-index), optional `branch` param |
| `/sync-all` | POST | Sync all registered branches (iterates checkout → pull → index) |
| `/rebuild` | POST | Full rebuild of a specific branch, optional `branch` param |
| `/rebuild-all` | POST | Full rebuild of all registered branches |
| `/unregister` | POST | Remove a repo |
| `/api/validate/{name}` | GET | Health check a repo |
| `/api/task/{task_id}` | GET | Poll async task progress |

Each registered repo can track multiple branches. Specify `branches: ["main", "develop"]` on register — `/sync-all` iterates all of them automatically. Vectors are isolated by `branch` metadata. Search returns results across all branches; the response includes a `branch` field to identify the source. Webhooks extract the branch from `ref` in push events, syncing only if it matches a registered branch.

### Search & Navigation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic search with query rewriting |
| `/trace` | POST | Trace call graph (up/down) |
| `/source` | POST | Get source context for a file range |
| `/api/repo/{name}` | GET | Repo detail |
| `/skill` | GET | Multi-repo merged skill file |

### Webhook Auto-Sync

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/{name}` | POST | **Recommended** — triggers sync by repo name |
| `/webhook` | POST | Generic — matches repo from payload |

After registering a repo, you get a webhook URL: `https://your-server.com/webhook/{name}`. Add this URL to your repository's webhook settings (push events) — each push automatically triggers a wiki sync.

Set `WEBHOOK_SECRET` env var for payload verification (HMAC-SHA256 for GitHub, Token header for GitLab).

### Search with Query Rewriting

By default, search calls LLM to expand your query into multiple precise phrases for better recall. Disable with `"rewrite": false`:

```json
{
  "query": "how does authentication work",
  "top_k": 10,
  "rewrite": true,
  "expand_depth": 1
}
```

Response includes `rewritten_queries` so you can see what was searched:

```json
{
  "results": [...],
  "total": 5,
  "rewritten_queries": ["how does authentication work", "authentication handler", "token verification", "login flow", "auth middleware"]
}
```

### API Authentication

When `REPO_WIKI_API_KEY` is set, all endpoints (except `/health` and `/webhook`) require an `Authorization: Bearer <key>` header.

---

## MCP Server

repo-wiki ships with a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server, allowing any MCP-capable LLM client — Claude Code, Cursor, Windsurf, VS Code + Copilot, and others — to search your codebase directly.

### Modes

```
repo-wiki serve              # Single-repo — reads local vector store
repo-wiki serve --api <URL>  # Multi-repo — proxies to REST API backend
```

**Single-Repo Mode:** Run directly inside an indexed repository. The MCP server reads the local `.indexer/vector_db` and configuration:

```bash
cd my-project
repo-wiki run              # index first
repo-wiki serve            # start MCP server (stdio transport)
```

Provides 3 tools:

| Tool | Description |
|------|-------------|
| `search_symbols_tool` | Semantic search for code symbols |
| `trace_call_tool` | Trace call graph (up/down) |
| `get_source_context_tool` | Get source code context |

**Multi-Repo Mode:** Proxies through the REST API, giving access to all registered repositories:

```bash
repo-wiki serve-api &                  # start REST API first
repo-wiki serve --api http://localhost:7654  # start MCP pointing at API
```

Adds a `list_repos` tool for discovering available repositories.

### Integration with LLM Clients

**Claude Code:**

```json
{
  "mcpServers": {
    "repo-wiki": {
      "command": "repo-wiki",
      "args": ["serve"]
    }
  }
}
```

Pointing to a remote REST API:

```json
{
  "mcpServers": {
    "repo-wiki": {
      "command": "repo-wiki",
      "args": ["serve", "--api", "http://localhost:7654"]
    }
  }
}
```

**Cursor / Windsurf / Copilot:** Similar configuration, point the command at `repo-wiki serve`. See your IDE's MCP configuration docs for details.

### Loading the Skill

The skill file lives at `.indexer/skills/codebase.md` after you run `repo-wiki run`. Load it into your agent once — it activates automatically on any codebase question.

**Claude Code:**

```bash
# Global — available in every project
mkdir -p ~/.claude/skills/codebase
cp .indexer/skills/codebase.md ~/.claude/skills/codebase/SKILL.md

# Project-local — available in this repo only
mkdir -p .claude/skills/codebase
cp .indexer/skills/codebase.md .claude/skills/codebase/SKILL.md
```

**Cursor / Windsurf / Copilot / Zed:** Same as kiwiskil — see the [original instructions](https://github.com/ximihoque/kiwiskil#loading-the-skill) for your specific editor.

---

## Configuration

### `.indexer.toml` (per-repo, created by `repo-wiki init`)

```toml
[llm]
provider = "openai/qwen-plus-2025-04-28"  # any LiteLLM-compatible model string
api_key_env = "DASHSCOPE_API_KEY"          # env var name, not the key itself
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

[indexer]
wiki_dir = "wiki"
ignore = ["node_modules", ".venv", "dist", "build", "__pycache__", "*.test.*"]
max_tokens_per_batch = 8000

[embedding]
provider = "dashscope/text-embedding-v4"
api_key_env = "DASHSCOPE_API_KEY"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
dimensions = 1024

[vector_store]
backend = "chromadb"
persist_dir = ".indexer/vector_db"
collection_name = "repo_wiki_code"

[hooks]
pre_commit = true
synthesize_commit_message = true
deep = true
```

Any LiteLLM-compatible provider works: OpenAI, Anthropic, Gemini, Ollama, local models.

### `.env` (server-level, for REST API / MCP mode)

```bash
# LLM
LLM_PROVIDER=openai/deepseek-v4-flash
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY_ENV=DASHSCOPE_API_KEY

# Embedding
EMBEDDING_PROVIDER=dashscope/text-embedding-v4
EMBEDDING_API_KEY_ENV=DASHSCOPE_API_KEY
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_DIMENSIONS=1024

# Vector DB
VECTOR_BACKEND=chromadb
VECTOR_PERSIST_DIR=.indexer/vector_db
VECTOR_COLLECTION_NAME=repo_wiki_code

# REST API Service
REPO_WIKI_API_KEY=                       # API auth key (requires Bearer Token)
PUBLIC_DOMAIN=https://your-server.com    # Public domain for webhook URL
WEBHOOK_SECRET=your-webhook-secret       # Webhook signature verification key
```

---

## Supported Languages

| Language | Status | Parser |
|----------|--------|--------|
| Python | Supported | stdlib `ast` |
| JavaScript (`.js`, `.jsx`, `.mjs`, `.cjs`) | Supported | tree-sitter |
| TypeScript (`.ts`, `.tsx`) | Supported | tree-sitter |
| Go | Supported | tree-sitter-go |
| Rust (`.rs`) | Supported | tree-sitter-rust |
| Java (`.java`) | Supported | tree-sitter-java |
| Ruby (`.rb`) | Supported | tree-sitter-ruby |

---

## Design Principles

- **Structural facts only** — wiki pages contain symbols, relationships, and entry points. No prose summaries, no architectural opinions. The client LLM draws its own conclusions.
- **Checked in, not served** — the wiki is plain markdown in your repo. It travels with your code, is tracked by git, and is readable by humans and agents alike.
- **Incremental by default** — git diff + content hash manifest means only changed files are re-processed on each commit.
- **Provider-agnostic** — LiteLLM means you can use any model, local or cloud, without changing the tool.
- **Search-ready** — vector embeddings and semantic search are first-class, not an add-on.

---

## License

MIT
