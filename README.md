# repo-wiki

**Your codebase, understood by any LLM.**

Generate a checked-in wiki, skill files, and vector search from any repo — no cloud, no lock-in.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![Forked from kiwiskil](https://img.shields.io/badge/forked%20from-kiwiskil-6366f1)](https://github.com/ximihoque/kiwiskil)

[Install](#install) · [Quick Start](#quick-start) · [REST API](#rest-api) · [CLI](#cli) · [Configuration](#configuration)

[中文文档](README_CN.md)

---

repo-wiki generates a structural wiki, skill files, and a vector search index from any codebase. It enables LLM agents to navigate code without reading source files — using a knowledge graph built from your repo and checked into git.

> **Forked from [kiwiskil](https://github.com/ximihoque/kiwiskil)** — repo-wiki extends the original with a REST API, vector search, query rewriting, repository health checks, and Go language support.

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
| Repository health checks | — | ✓ |
| Auto-repair on sync | — | ✓ |
| Go language support | — | ✓ |
| Async task processing | — | ✓ |

### REST API with Web UI

A full-featured REST API (`repo-wiki serve-api`) for remote repository management:

- **Register repos** via URL with git clone support (GitHub PAT, GitLab token, password auth)
- **Sync / Rebuild** repos with real-time progress tracking
- **Semantic search** across all registered repos via vector similarity
- **Call graph tracing** — follow calls up or down the dependency chain
- **Source context** — fetch specific line ranges from any tracked file
- **Web dashboard** — manage repos, browse wiki pages, search symbols from a browser

### Vector Search (RAG-ready)

- **ChromaDB** stores embeddings for every indexed symbol
- **Semantic search** returns results ranked by vector distance, not just text match
- **Query rewriting** — LLM expands natural language queries into multiple precise search phrases for better recall (e.g. `"how does auth work"` → `["authentication handler", "token verification", "login flow", ...]`)
- **Call graph expansion** — automatically includes related symbols from the call chain

### Repository Health Checks & Repair

- **Validate** endpoint checks: config file, manifest, wiki pages, skill file, vector DB, stale files
- **Auto-repair** on sync: missing wiki pages, missing vector DB, stale index entries are all detected and fixed
- **Manifest path fixup**: corrects wiki page path inconsistencies between manifest and actual files

### Go Language Support

AST parsing for Go via tree-sitter-go — extracts functions, methods, types, interfaces, and call relationships.

### Async Task Processing

Repository registration, sync, and rebuild run as background tasks with real-time progress updates (step name + percentage). The API responds immediately with a task ID.

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

# Register a repo (clones + indexes)
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git"}'

# Search across repos
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "authentication middleware", "top_k": 10}'

# Open the web dashboard
open http://localhost:7654
```

---

## REST API

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/repos` | GET | List all registered repos |
| `/register` | POST | Register & index a repo from URL |
| `/sync` | POST | Sync a repo (pull + re-index changes) |
| `/rebuild` | POST | Full rebuild (delete + re-index) |
| `/unregister` | POST | Remove a repo |
| `/api/validate/{name}` | GET | Health check a repo |
| `/api/task/{task_id}` | GET | Poll async task progress |

### Search & Navigation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic search with query rewriting |
| `/trace` | POST | Trace call graph (up/down) |
| `/source` | POST | Get source context for a file range |
| `/api/repo/{name}` | GET | Repo detail (wiki pages, manifest) |

### Search with Query Rewriting

By default, search calls LLM to expand your query into multiple precise phrases for better recall. Disable with `"rewrite": false`:

```json
{
  "query": "how does authentication work",
  "repo": "my-project",
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

---

## CLI

```bash
repo-wiki init              # set up config, hook, and CLAUDE.md
repo-wiki run               # smart incremental + deep enrichment (default)
repo-wiki run --skip-deep   # skip narrative/flows/constraints enrichment (faster)
repo-wiki run --force       # force full re-index of all files
repo-wiki run --staged      # incremental on staged files only (used by hook)
repo-wiki status            # show last indexed commit, stale files, stats
repo-wiki hook install      # manually install pre-commit hook
repo-wiki hook remove       # remove pre-commit hook
repo-wiki serve-api         # start REST API server with web dashboard
repo-wiki mcp               # start MCP server for semantic code search
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

ChromaDB vector store containing embeddings for every indexed symbol. Used by the REST API for semantic search.

---

## Loading the Skill

The skill file lives at `.indexer/skills/codebase.md` after you run `repo-wiki run`. Load it into your agent once — it activates automatically on any codebase question.

### Claude Code

```bash
# Global — available in every project
mkdir -p ~/.claude/skills/codebase
cp .indexer/skills/codebase.md ~/.claude/skills/codebase/SKILL.md

# Project-local — available in this repo only
mkdir -p .claude/skills/codebase
cp .indexer/skills/codebase.md .claude/skills/codebase/SKILL.md
```

### Cursor / Windsurf / Copilot / Zed

Same as kiwiskil — see the [original instructions](https://github.com/ximihoque/kiwiskil#loading-the-skill) for your specific editor.

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

### `.env` (server-level, for REST API mode)

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
```

---

## Supported Languages

| Language | Status | Parser |
|----------|--------|--------|
| Python | Supported | stdlib `ast` |
| JavaScript (`.js`, `.jsx`, `.mjs`, `.cjs`) | Supported | tree-sitter |
| TypeScript (`.ts`, `.tsx`) | Supported | tree-sitter |
| Go | Supported | tree-sitter-go |
| Rust, Java, Ruby | Planned | tree-sitter |

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
