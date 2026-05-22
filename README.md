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

从源码安装（未发布到 PyPI 时）：

```bash
git clone https://github.com/xzf475/repo-wiki.git
cd repo-wiki
pip install -e .
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
repo-wiki agent capabilities # 输出 Agent 工具能力清单
repo-wiki agent schema       # 输出 OpenAPI/JSON Schema 契约
repo-wiki agent context --symbol-id src/auth.py::validate_token
repo-wiki agent plan --goal "fix token validation" --symbol-id src/auth.py::validate_token
repo-wiki agent verify       # 基于本地 git diff 生成提交前验证建议
repo-wiki agent diagnose     # 诊断 manifest/wiki/vector/source/freshness
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
git clone https://github.com/xzf475/repo-wiki.git && cd repo-wiki
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

### MCP 工具

| MCP 工具 | 说明 | 可用模式 |
|----------|------|----------|
| `search_symbols_tool` | 语义搜索代码符号（支持 LLM 查询改写） | 单仓库 / 多仓库 |
| `resolve_symbol_tool` | 将自然语言/符号名/文件提示解析为具体 `component_id` | 单仓库 / 多仓库 |
| `trace_call_tool` | 追踪调用链（向上/向下） | 单仓库 / 多仓库 |
| `get_source_context_tool` | 获取源码上下文 | 单仓库 / 多仓库 |
| `get_edit_context_tool` | 获取修改前上下文包（源码、调用方、被调方、同文件符号、候选测试、索引状态） | 单仓库 / 多仓库 |
| `find_tests_for_symbol_tool` | 查找符号相关测试文件 | 单仓库 / 多仓库 |
| `pre_edit_check_tool` | 修改前检查（索引状态、dirty 文件、候选测试、推荐命令、影响范围） | 单仓库 / 多仓库 |
| `impact_analysis_tool` | 分析符号变更影响面（调用方、被调方、入口点、测试、风险） | 单仓库 / 多仓库 |
| `change_plan_tool` | 为目标和符号生成 Agent 修改计划（读文件、改动目标、验证命令、风险） | 单仓库 / 多仓库 |
| `diagnose_index_tool` | 诊断索引完整性（manifest、wiki、vector DB、源码缺失、新鲜度） | 单仓库 / 多仓库 |
| `agent_protocol_tool` | 输出 Codex/Claude 友好的紧凑协议字段 | 单仓库 / 多仓库 |
| `locate_from_error_tool` | 从 stack trace、错误日志、HTTP path 定位代码候选 | 单仓库 / 多仓库 |
| `list_entry_points_tool` | 列出 API/CLI/event/job/webhook 入口点 | 单仓库 / 多仓库 |
| `post_edit_verify_tool` | 修改后提交前验证建议；本地自动读 `git diff`，远程可传 diff | 单仓库 / 多仓库 |
| `change_set_tool` | 从目标、符号或 diff 推导必须一起改的文件/符号集合 | 单仓库 / 多仓库 |
| `coverage_map_tool` | 反查源码符号与候选测试覆盖关系 | 单仓库 / 多仓库 |
| `index_diff_report_tool` | 对比索引快照中的符号、入口点、调用图变化 | 单仓库 / 多仓库 |
| `cross_repo_graph_tool` | 构建跨仓依赖图（如 frontend client → backend route） | 多仓库 |
| `stable_symbol_id_tool` | 生成稳定符号 ID，辅助重命名/移动追踪 | 单仓库 / 多仓库 |
| `agent_capabilities_manifest_tool` | 输出 Agent 工具能力清单和推荐调用顺序 | 单仓库 / 多仓库 |
| `get_index_status_tool` | 检查索引是否过期及原因 | 单仓库 / 多仓库 |
| `list_repos` | 列出所有已注册仓库（含分支、索引提交、统计） | 多仓库 |

### 单仓库模式

```bash
cd my-project
repo-wiki run
repo-wiki serve           # stdio 模式，提供 3 个工具
```

| MCP 工具 | 说明 |
|----------|------|
| `search_symbols_tool` | 语义搜索代码符号 |
| `resolve_symbol_tool` | 解析具体 `component_id` |
| `trace_call_tool` | 追踪调用链 |
| `get_source_context_tool` | 获取源码上下文 |
| `get_edit_context_tool` | 获取修改前上下文包 |
| `find_tests_for_symbol_tool` | 查找符号相关测试文件 |
| `pre_edit_check_tool` | 修改前检查 |
| `impact_analysis_tool` | 分析变更影响面 |
| `change_plan_tool` | 生成修改计划 |
| `diagnose_index_tool` | 诊断索引健康度 |
| `agent_protocol_tool` | 输出 Agent 紧凑协议 |
| `locate_from_error_tool` | 从错误日志定位代码 |
| `list_entry_points_tool` | 列出入口点 |
| `post_edit_verify_tool` | 修改后验证建议 |
| `change_set_tool` | 推导必须一起改的集合 |
| `coverage_map_tool` | 测试覆盖反查 |
| `index_diff_report_tool` | 索引差异报告 |
| `cross_repo_graph_tool` | 跨仓依赖图 |
| `stable_symbol_id_tool` | 生成稳定符号 ID |
| `agent_capabilities_manifest_tool` | 工具能力清单 |
| `get_index_status_tool` | 检查索引是否过期 |

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

> **认证**：设置了 `MCP_API_KEY` 时，客户端需在请求头中添加 `Authorization: Bearer <key>`。
> **DNS 反绑定保护**：MCP SDK 默认只接受 `localhost`/`127.0.0.1` 的 Host 头。
> 远程访问时 SDK 会自动关闭该保护，无需额外配置。

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

项目中还提供了 **repo-wiki MCP Agent 技能**（`skills/SKILL.md`），让 AI Agent 学会通过 MCP 工具自动进行语义搜索、调用链追踪和源码阅读。安装方式：

```bash
# 复制到 Trae/Claude Code 技能目录
cp -r skills ~/.trae-cn/skills/repo-wiki-code-analysis

# 或通过 npx skills 安装
npx skills add /path/to/repo-wiki -g -y
```

---

## API 端点

### 仓库管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/repos` | GET | 列出所有已注册仓库 |
| `/register` | POST | 注册并索引仓库。支持 `branches` 数组、`branch` 字符串或 `branch_rule` 通配符规则（如 `release/*`、`feature/*`）。默认 `["main"]` |
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
| `/resolve-symbol` | POST | 将自然语言/符号名/文件提示解析为具体 `component_id` |
| `/trace` | POST | 追踪调用链（向上/向下） |
| `/source` | POST | 获取文件指定行范围的源码 |
| `/edit-context` | POST | 获取修改前上下文包 |
| `/tests-for-symbol` | POST | 查找符号相关测试文件 |
| `/pre-edit-check` | POST | 修改前检查并返回推荐测试命令 |
| `/impact-analysis` | POST | 分析符号变更影响面 |
| `/change-plan` | POST | 生成 Agent 修改计划 |
| `/diagnose-index` | POST | 诊断索引完整性和新鲜度 |
| `/agent-protocol` | POST | 返回 Codex/Claude 友好的紧凑字段 |
| `/locate-from-error` | POST | 从 stack trace、错误日志、HTTP path 定位代码候选 |
| `/entry-points` | POST | 列出 API/CLI/event/job/webhook 入口点 |
| `/post-edit-verify` | POST | 基于 diff/changed_files 生成提交前验证建议 |
| `/change-set` | POST | 推导必须一起改的文件/符号集合 |
| `/coverage-map` | POST | 反查源码符号候选测试覆盖 |
| `/index-diff-report` | POST | 对比索引快照变化 |
| `/cross-repo-graph` | POST | 构建跨仓依赖图 |
| `/stable-symbol-id` | POST | 生成稳定符号 ID |
| `/agent-capabilities` | GET/POST | Agent 工具能力清单 |
| `/agent-schema` | GET/POST | Agent API 的 OpenAPI 3.1 / JSON Schema 契约 |
| `/index-status` | POST | 检查索引是否过期 |
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
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_DIMENSIONS=1024

# 向量数据库
VECTOR_BACKEND=chromadb
VECTOR_PERSIST_DIR=.indexer/vector_db
VECTOR_COLLECTION_NAME=repo_wiki_code

# REST API
API_PORT=7654
REPO_WIKI_API_KEY=                     # API 认证密钥
PUBLIC_DOMAIN=https://your-server.com  # 公开域名，用于 webhook URL
WEBHOOK_SECRET=your-webhook-secret     # Webhook 签名密钥

# MCP 服务器
MCP_ENABLED=false                      # 是否同时启动 MCP 服务器（streamable-http）
MCP_PORT=8000                          # MCP 服务器端口
MCP_API_KEY=                           # MCP 认证密钥（可选，设置后需 Bearer Token）
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
