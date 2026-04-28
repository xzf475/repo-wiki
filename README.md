# repo-wiki

**让任何 LLM 理解你的代码库。**

从任意仓库生成可提交的 Wiki、技能文件和向量检索索引。Fork 自 [kiwiskil](https://github.com/ximihoque/kiwiskil)，增加了 REST API、ChromaDB 语义搜索、查询改写、调用链追踪、Webhook 自动同步、MCP 服务器以及 Rust/Java/Ruby/Go 支持。

[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README_EN.md)

---

## 目录

- [工作原理](#工作原理)
- [安装](#安装)
- [CLI 模式](#cli-模式)
- [REST API 模式](#rest-api-模式)
- [Docker 部署](#docker-部署)
- [MCP 服务器](#mcp-服务器)
- [API 端点](#api-端点)
- [配置](#配置)
- [支持的语言](#支持的语言)

---

## 工作原理

1. **AST 解析** — 从源文件提取符号、导入和调用图
2. **LLM 描述** — 通过 LiteLLM 使用任意模型为每个符号生成一行描述
3. **密度分组** — 按逻辑密度将文件组织为 Wiki 页面
4. **Embedding** — 为每个符号生成向量，存入 ChromaDB
5. **技能文件** — 生成 `.indexer/skills/codebase.md`，让任何 LLM Agent 能导航代码库

输出产物：`wiki/`（结构化 Markdown）、`.indexer/manifest.json`（符号清单）、`.indexer/skills/codebase.md`（Agent 技能文件）、`.indexer/vector_db/`（向量检索索引）。

---

## 安装

```bash
pip install repo-wiki
```

---

## CLI 模式

```bash
repo-wiki init              # 创建 .indexer.toml，安装 pre-commit hook
repo-wiki run               # 生成 wiki/ 和 skill（默认启用深度增强）
repo-wiki run --skip-deep   # 跳过 LLM 增强（更快）
repo-wiki run --force       # 强制全量重新索引
repo-wiki run --staged      # 仅对暂存文件增量索引（hook 使用）
repo-wiki status            # 显示上次索引提交、过期文件、统计
repo-wiki hook install      # 手动安装 pre-commit hook
repo-wiki hook remove       # 移除 pre-commit hook
repo-wiki serve             # 启动 MCP 服务器
```

每次提交时 pre-commit hook 自动运行 `repo-wiki run --staged`，仅重新索引变更文件。

**深度增强**（默认启用）：使用 LLM 生成系统概述、关键请求流程和设计约束，写入 `wiki/INDEX.md` 和技能文件。速度优先时使用 `--skip-deep`。

---

## REST API 模式

```bash
# 启动服务
repo-wiki serve-api --port 7654

# 注册仓库（克隆 + 索引 + 返回 webhook URL）
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'

# 跨仓库语义搜索
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "认证中间件", "top_k": 10}'
```

Web 仪表盘：[http://localhost:7654](http://localhost:7654)

---

## Docker 部署

```bash
git clone https://github.com/your/repo-wiki.git && cd repo-wiki
cp .env.example .env          # 填入 API Key
docker compose up -d          # 构建并启动
docker compose logs -f        # 查看日志
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'
docker compose down           # 停止
```

- `.env` 放在项目根目录，`docker-compose.yml` 自动挂载
- 索引数据持久化在 Docker volume 中
- 首次构建约 2-3 分钟（编译 tree-sitter），后续 `docker compose up -d --build` 仅重建变更层
- 仅修改 `.env` 时 `docker compose restart` 即可

---

## MCP 服务器

repo-wiki 提供 [MCP](https://modelcontextprotocol.io) 服务器，让支持 MCP 的 LLM 客户端直接搜索你的代码库。

### 单仓库模式

```bash
cd my-project
repo-wiki run
repo-wiki serve           # stdio 模式，提供 3 个工具
```

| MCP 工具 | 说明 |
|----------|------|
| `search_symbols_tool` | 语义搜索代码符号 |
| `trace_call_tool` | 追踪调用链 |
| `get_source_context_tool` | 获取源码上下文 |

### 多仓库模式

```bash
repo-wiki serve-api &                    # 先启动 REST API
repo-wiki serve --api http://localhost:7654  # MCP 代理到 API
```

额外提供 `list_repos` 工具。

### 客户端配置

**本地安装模式**（已 `pip install repo-wiki`）：

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

**npx 模式**（无需安装，即用即走）：

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

远程模式将 args 改为 `["-y", "repo-wiki", "serve", "--api", "http://localhost:7654"]`。

**远程服务器模式**（本地无 repo-wiki，服务端在云端部署）：

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

设置了 `MCP_API_KEY` 时，客户端需在请求头中添加 `Authorization: Bearer <key>`。根据不同 MCP 客户端配置方式，可能需要增加 headers 字段或使用 CLI 参数传入 Token。

服务端启动方式：

```bash
# 在云端服务器上运行
repo-wiki serve-api --port 7654 &                          # REST API
repo-wiki serve --transport streamable-http --port 8000 --api http://localhost:7654  # MCP HTTP
```

### 加载技能文件

```bash
# 全局可用
mkdir -p ~/.claude/skills/codebase
cp .indexer/skills/codebase.md ~/.claude/skills/codebase/SKILL.md
```

---

## API 端点

### 仓库管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/repos` | GET | 列出所有已注册仓库 |
| `/register` | POST | 注册并索引仓库。支持 `branches` 数组或 `branch` 字符串，默认 `["main"]` |
| `/sync` | POST | 增量同步指定分支，可选 `branch` 参数 |
| `/sync-all` | POST | 同步所有已注册分支 |
| `/rebuild` | POST | 全量重建指定分支 |
| `/rebuild-all` | POST | 全量重建所有已注册分支 |
| `/unregister` | POST | 移除仓库 |
| `/api/validate/{name}` | GET | 仓库健康检查 |
| `/api/task/{task_id}` | GET | 轮询异步任务进度 |

### 搜索与导航

| 端点 | 方法 | 说明 |
|------|------|------|
| `/search` | POST | 语义搜索（默认启用 LLM 查询改写，设置 `"rewrite":false` 关闭） |
| `/trace` | POST | 追踪调用链（向上/向下） |
| `/source` | POST | 获取文件指定行范围的源码 |
| `/api/repo/{name}` | GET | 仓库详情 |
| `/skill` | GET | 多仓库合并技能文件 |

### Webhook

| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/{name}` | POST | 自动触发同步。URL 模板：`https://your-server.com/webhook/{name}?sign={sign}`，通过 `WEBHOOK_SECRET` 生成 |

### 认证

设置 `REPO_WIKI_API_KEY` 后，除 `/health` 和 `/webhook/` 开头的路径外所有端点需 `Authorization: Bearer <key>` 头。

---

## 配置

### `.indexer.toml`（每仓库，`repo-wiki init` 创建）

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

支持任何 LiteLLM 兼容的提供商：OpenAI、Anthropic、Gemini、Ollama 等。

### `.env`（REST API / MCP 模式）

```bash
# LLM
LLM_PROVIDER=openai/deepseek-v4-flash
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY_ENV=DASHSCOPE_API_KEY

# Embedding
EMBEDDING_PROVIDER=dashscope/text-embedding-v4
EMBEDDING_API_KEY_ENV=DASHSCOPE_API_KEY
EMBEDDING_DIMENSIONS=1024

# 向量数据库
VECTOR_BACKEND=chromadb
VECTOR_PERSIST_DIR=.indexer/vector_db
VECTOR_COLLECTION_NAME=repo_wiki_code

# REST API
REPO_WIKI_API_KEY=                     # API 认证密钥
PUBLIC_DOMAIN=https://your-server.com  # 公开域名，用于 webhook URL
WEBHOOK_SECRET=your-webhook-secret     # Webhook 签名密钥
```

---

## 支持的语言

| 语言 | 解析器 |
|------|--------|
| Python | stdlib `ast` |
| JavaScript / TypeScript | tree-sitter |
| Go | tree-sitter-go |
| Rust | tree-sitter-rust |
| Java | tree-sitter-java |
| Ruby | tree-sitter-ruby |

---

## 许可证

MIT
