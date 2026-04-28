# repo-wiki

**Your codebase, understood by any LLM.**

Generate a checked-in wiki, skill files, and vector search index from any repo. Forked from [kiwiskil](https://github.com/ximihoque/kiwiskil), adds REST API, ChromaDB semantic search, query rewriting, call graph tracing, webhook auto-sync, MCP server, and Rust/Java/Ruby/Go support.

[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[中文文档](README.md)

---

## Table of Contents

- [How It Works](#how-it-works)
- [Install](#install)
- [CLI Mode](#cli-mode)
- [REST API Mode](#rest-api-mode)
- [Docker](#docker)
- [MCP Server](#mcp-server)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Supported Languages](#supported-languages)

---

## How It Works

1. **AST parsing** — extracts symbols, imports, and call graphs from source files
2. **LLM descriptions** — generates one-line descriptions per symbol via LiteLLM (any provider)
3. **Density-based grouping** — organizes files into wiki pages by logical density
4. **Embedding** — generates vectors for every symbol, stored in ChromaDB
5. **Skill file** — generates `.indexer/skills/codebase.md` so any LLM agent can navigate your codebase

Output: `wiki/` (structured markdown), `.indexer/manifest.json` (symbol manifest), `.indexer/skills/codebase.md` (agent skill file), `.indexer/vector_db/` (vector search index).

---

## Install

```bash
pip install repo-wiki
```

---

## CLI Mode

```bash
repo-wiki init               # create .indexer.toml, install pre-commit hook
repo-wiki run                # generate wiki/ and skill (deep enrichment enabled by default)
repo-wiki run --skip-deep    # skip LLM enrichment (faster)
repo-wiki run --force        # force full re-index
repo-wiki run --staged       # incremental on staged files only (hook)
repo-wiki status             # show last indexed commit, stale files, stats
repo-wiki hook install       # manually install pre-commit hook
repo-wiki hook remove        # remove pre-commit hook
repo-wiki serve              # start MCP server
```

The pre-commit hook runs `repo-wiki run --staged` on every commit — only changed files are re-indexed.

**Deep enrichment** (default): Uses your LLM to generate system overview, key request flows, and design constraints — written into `wiki/INDEX.md` and the skill file. Use `--skip-deep` for structural-only indexing when speed matters.

---

## REST API Mode

```bash
# Start the server
repo-wiki serve-api --port 7654

# Register a repo (clones + indexes + returns webhook URL)
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'

# Semantic search across repos
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "authentication middleware", "top_k": 10}'
```

Web dashboard: [http://localhost:7654](http://localhost:7654)

---

## Docker

```bash
git clone https://github.com/your/repo-wiki.git && cd repo-wiki
cp .env.example .env          # fill in your API keys
docker compose up -d          # build & start
docker compose logs -f        # follow logs
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'
docker compose down           # stop
```

- `.env` goes in the project root — `docker-compose.yml` mounts it automatically
- Index data is persisted in Docker volumes
- First build takes ~2-3 min (compiles tree-sitter); subsequent: `docker compose up -d --build`
- For `.env` changes only: `docker compose restart`

---

## MCP Server

repo-wiki provides an [MCP](https://modelcontextprotocol.io) server, letting MCP-capable LLM clients search your codebase directly.

### Single-Repo Mode

```bash
cd my-project
repo-wiki run
repo-wiki serve           # stdio mode, provides 3 tools
```

| MCP Tool | Description |
|----------|-------------|
| `search_symbols_tool` | Semantic search for code symbols |
| `trace_call_tool` | Trace call graph (up/down) |
| `get_source_context_tool` | Get source code context |

### Multi-Repo Mode

```bash
repo-wiki serve-api &                    # start REST API first
repo-wiki serve --api http://localhost:7654  # MCP proxies to API
```

Adds a `list_repos` tool.

### Client Configuration

**Local install** (`pip install repo-wiki`):

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

**npx mode** (no install required):

```json
{
  "mcpServers": {
    "repo-wiki": {
      "command": "npx",
      "args": ["-y", "repo-wiki", "serve"]
    }
  }
}
```

For remote mode: `"args": ["-y", "repo-wiki", "serve", "--api", "http://localhost:7654"]`.

**Remote server mode** (no local install, server deployed in cloud):

```json
{
  "mcpServers": {
    "repo-wiki": {
      "url": "http://your-server.com:8000/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Server-side startup:

```bash
# Run these on your cloud server
repo-wiki serve-api --port 7654 &
repo-wiki serve --transport streamable-http --port 8000 --api http://localhost:7654
```

### Loading the Skill

```bash
mkdir -p ~/.claude/skills/codebase
cp .indexer/skills/codebase.md ~/.claude/skills/codebase/SKILL.md
```

---

## API Endpoints

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/repos` | GET | List all registered repos |
| `/register` | POST | Register & index a repo. Accepts `branches` array or `branch` string, defaults to `["main"]` |
| `/sync` | POST | Sync a specific branch, optional `branch` param |
| `/sync-all` | POST | Sync all registered branches |
| `/rebuild` | POST | Full rebuild of a specific branch |
| `/rebuild-all` | POST | Full rebuild of all registered branches |
| `/unregister` | POST | Remove a repo |
| `/api/validate/{name}` | GET | Health check a repo |
| `/api/task/{task_id}` | GET | Poll async task progress |

### Search & Navigation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic search (LLM query rewriting enabled by default, use `"rewrite":false` to disable) |
| `/trace` | POST | Trace call graph (up/down) |
| `/source` | POST | Get source context for a file range |
| `/api/repo/{name}` | GET | Repo detail |
| `/skill` | GET | Multi-repo merged skill file |

### Webhook

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/{name}` | POST | Triggers sync by repo name. URL template: `https://your-server.com/webhook/{name}?sign={sign}`, generated from `WEBHOOK_SECRET` |

### Authentication

When `REPO_WIKI_API_KEY` is set, all endpoints (except `/health` and paths starting with `/webhook/`) require `Authorization: Bearer <key>`.

---

## Configuration

### `.indexer.toml` (per-repo, created by `repo-wiki init`)

```toml
[llm]
provider = "openai/qwen-plus-2025-04-28"
api_key_env = "DASHSCOPE_API_KEY"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

[indexer]
wiki_dir = "wiki"
ignore = ["node_modules", ".venv", "dist", "build", "__pycache__", "*.test.*"]
max_tokens_per_batch = 8000

[embedding]
provider = "dashscope/text-embedding-v4"
api_key_env = "DASHSCOPE_API_KEY"
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

Any LiteLLM-compatible provider works: OpenAI, Anthropic, Gemini, Ollama, etc.

### `.env` (REST API / MCP mode)

```bash
# LLM
LLM_PROVIDER=openai/deepseek-v4-flash
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY_ENV=DASHSCOPE_API_KEY

# Embedding
EMBEDDING_PROVIDER=dashscope/text-embedding-v4
EMBEDDING_API_KEY_ENV=DASHSCOPE_API_KEY
EMBEDDING_DIMENSIONS=1024

# Vector DB
VECTOR_BACKEND=chromadb
VECTOR_PERSIST_DIR=.indexer/vector_db
VECTOR_COLLECTION_NAME=repo_wiki_code

# REST API
REPO_WIKI_API_KEY=                       # API auth key
PUBLIC_DOMAIN=https://your-server.com    # Public domain for webhook URL
WEBHOOK_SECRET=your-webhook-secret       # Webhook signature key
```

---

## Supported Languages

| Language | Parser |
|----------|--------|
| Python | stdlib `ast` |
| JavaScript / TypeScript | tree-sitter |
| Go | tree-sitter-go |
| Rust | tree-sitter-rust |
| Java | tree-sitter-java |
| Ruby | tree-sitter-ruby |

---

## License

MIT
