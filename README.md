# repo-wiki

**让任何 LLM 理解你的代码库。**

从任意仓库生成可提交的 Wiki、技能文件和向量检索——无需上云，无厂商锁定。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![Forked from kiwiskil](https://img.shields.io/badge/forked%20from-kiwiskil-6366f1)](https://github.com/ximihoque/kiwiskil)

[English](README_EN.md)

---

repo-wiki 从任意代码库生成可提交的结构化 Wiki、技能文件和向量检索索引。它让 LLM Agent 无需阅读源码即可导航代码——使用从你的仓库构建并提交到 Git 的知识图谱。

> **Fork 自 [kiwiskil](https://github.com/ximihoque/kiwiskil)** — repo-wiki 在原版基础上增加了 REST API、向量检索、查询改写、仓库健康检查、Webhook 自动同步以及 Rust/Java/Ruby/Go 语言支持。

---

## 工作原理

1. **AST 解析** — 从源文件提取符号、导入和调用图
2. **LLM 描述** — 通过 LiteLLM 使用任意模型为每个符号生成一行描述
3. **密度分组** — 按逻辑密度（而非目录结构）将文件组织为 Wiki 页面
4. **Embedding** — 为每个符号生成向量表示
5. **ChromaDB** — 存储和索引向量，支持快速语义搜索
6. **Pre-commit Hook** — 每次提交自动保持 Wiki 同步
7. **技能文件** — 生成 `.indexer/skills/codebase.md`，让任何 LLM Agent 能导航你的代码库

Wiki 是纯 Markdown，提交到你的仓库。无需云服务，无厂商锁定。

---

## 与 kiwiskil 的区别

| 功能 | kiwiskil | repo-wiki |
|------|----------|-----------|
| 结构化 Wiki + 技能文件 | ✓ | ✓ |
| Pre-commit Hook | ✓ | ✓ |
| REST API + Web 管理界面 | — | ✓ |
| 向量检索（ChromaDB） | — | ✓ |
| 查询改写 | — | ✓ |
| 调用链追踪 | — | ✓ |
| 仓库健康检查 | — | ✓ |
| 同步时自动修复 | — | ✓ |
| Webhook 自动同步 | — | ✓ |
| MCP 服务器 | — | ✓ |
| Rust / Java / Ruby / Go | — | ✓ |
| 异步任务处理 | — | ✓ |

---

## 安装

```bash
pip install repo-wiki
```

---

## 快速开始

### CLI 模式（单仓库）

```bash
# 在任意 Git 仓库中
repo-wiki init       # 创建 .indexer.toml，安装 pre-commit hook，追加 CLAUDE.md
repo-wiki run        # 生成 wiki/ 和 .indexer/skills/codebase.md
```

后续每次提交时，pre-commit hook 自动运行 `repo-wiki run --staged`——仅重新索引变更文件。

### REST API 模式（多仓库）

```bash
# 启动 API 服务
repo-wiki serve-api --port 7654

# 注册远程仓库（克隆 + 索引）
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git", "token": "ghp_xxx"}'
# 返回包含 webhook_url，可直接在 GitHub 中配置自动同步

# 跨仓库语义搜索
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "认证中间件", "top_k": 10}'

# Web 仪表盘
open http://localhost:7654
```

### MCP 模式（LLM Agent 集成）

```bash
# 单仓库模式——直接使用本地向量库
repo-wiki serve

# 多仓库模式——连接 REST API 后端
repo-wiki serve --api http://localhost:7654
```

详见 [MCP 服务器](#mcp-服务器) 章节。

---

## REST API

### 仓库管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/repos` | GET | 列出所有已注册仓库 |
| `/register` | POST | 通过 URL 注册并索引仓库，支持 `branches` 数组或 `branch` 单字符串，默认 `["main"]` |
| `/sync` | POST | 同步指定分支（git pull + 增量索引），可选 `branch` 参数 |
| `/sync-all` | POST | 同步所有已注册分支（依次 checkout → pull → 索引） |
| `/rebuild` | POST | 全量重建指定分支，可选 `branch` 参数 |
| `/rebuild-all` | POST | 全量重建所有已注册分支 |
| `/unregister` | POST | 移除仓库 |
| `/api/validate/{name}` | GET | 仓库健康检查 |
| `/api/task/{task_id}` | GET | 轮询异步任务进度 |

每个注册仓库可追踪多个分支。注册时指定 `branches: ["main", "develop"]`，后续 `/sync-all` 自动遍历所有分支。

向量索引按 `branch` 元数据隔离——搜索时跨分支返回结果，响应中包含 `branch` 字段可区分来源。webhook 自动从 push 事件的 `ref` 提取分支名，仅同步已注册的分支。

### 搜索与导航

| 端点 | 方法 | 说明 |
|------|------|------|
| `/search` | POST | 语义搜索（含查询改写） |
| `/trace` | POST | 追踪调用链（向上/向下） |
| `/source` | POST | 获取文件指定行范围的源码 |
| `/api/repo/{name}` | GET | 仓库详情 |
| `/skill` | GET | 多仓库合并技能文件 |

### Webhook 自动同步

| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/{name}` | POST | **推荐**——按仓库名自动触发同步 |
| `/webhook` | POST | 通用端点，解析 payload 匹配仓库 |

注册仓库后返回独立 webhook URL：`https://your-server.com/webhook/{name}`。直接在 GitHub/GitLab/Gitee 仓库设置中配置该 URL，后续每次 push 自动触发 wiki 更新。

通过 `WEBHOOK_SECRET` 环境变量启用签名验证——GitHub 使用 HMAC-SHA256，GitLab 使用 Token 头。

### 查询改写搜索

搜索默认调用 LLM 将查询扩展为多个精确检索词。可通过 `"rewrite": false` 关闭：

```json
{
  "query": "认证怎么处理的",
  "top_k": 10,
  "rewrite": true,
  "expand_depth": 1
}
```

响应中包含 `rewritten_queries`，可查看实际搜索了哪些词：

```json
{
  "results": ["..."],
  "total": 5,
  "rewritten_queries": ["认证怎么处理的", "认证处理", "Authentication handler", "token verification", "login authentication"]
}
```

### API 认证

设置环境变量 `REPO_WIKI_API_KEY` 后，除 `/health` 和 `/webhook` 外的所有端点需要 `Authorization: Bearer <key>` 头。

---

## MCP 服务器

repo-wiki 提供 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 服务器，让任何支持 MCP 的 LLM 客户端（Claude Code、Cursor、Windsurf、VS Code + Copilot 等）可以直接搜索你的代码库。

### 两种运行模式

```
repo-wiki serve              # 单仓库模式——直接读取本地向量库
repo-wiki serve --api <URL>  # 多仓库模式——连接 REST API 后端
```

#### 单仓库模式

在已索引的仓库中直接运行，MCP 服务器读取本地的 `.indexer/vector_db` 和配置：

```bash
cd my-project
repo-wiki run              # 先完成索引
repo-wiki serve            # 启动 MCP 服务器（stdio 模式）
```

提供 3 个工具：

| 工具 | 说明 |
|------|------|
| `search_symbols_tool` | 语义搜索代码符号 |
| `trace_call_tool` | 追踪调用链 |
| `get_source_context_tool` | 获取源码上下文 |

#### 多仓库模式

通过 MCP 代理访问 REST API，可以搜索所有已注册的仓库：

```bash
repo-wiki serve-api &                  # 先启动 REST API
repo-wiki serve --api http://localhost:7654  # 启动 MCP 指向 API
```

额外提供 `list_repos` 工具用于发现可用仓库。

### 集成到 LLM 客户端

**Claude Code：**

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

使用 `--api` 指向远程 REST API 时：

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

**Cursor / Windsurf / Copilot：**

类似配置，将命令指向 `repo-wiki serve`。详细集成步骤参见各 IDE 的 MCP 配置文档。

### 工作原理

MCP 服务器将 repo-wiki 的检索能力封装为标准 MCP 工具。当 LLM 需要理解代码时，自动调用这些工具——无需手动阅读源代码，Agent 通过搜索 + 追踪 + 源码获取即可完成任务。多仓库模式下进一步解耦，MCP 服务器作为轻量代理，检索逻辑在 REST API 端执行。

---

## CLI

```bash
repo-wiki init              # 初始化配置、hook 和 CLAUDE.md
repo-wiki run               # 智能增量索引 + 深度增强（默认）
repo-wiki run --skip-deep   # 跳过叙述/流程/约束增强（更快）
repo-wiki run --force       # 强制全量重新索引
repo-wiki run --staged      # 仅对暂存文件增量索引（hook 使用）
repo-wiki status            # 显示上次索引提交、过期文件、统计
repo-wiki hook install      # 手动安装 pre-commit hook
repo-wiki hook remove       # 移除 pre-commit hook
repo-wiki serve             # 启动 MCP 服务器
repo-wiki serve-api         # 启动 REST API 服务和 Web 仪表盘
```

### 深度模式

默认情况下，`repo-wiki run` 在结构化索引后执行**深度增强**。使用你配置的 LLM 生成：

- **系统叙述** — 代码库功能的自然语言概述
- **关键请求流程** — 跨模块的端到端数据流
- **设计约束** — 每个模块的注意事项、不变量和非显而易见的规则

这些内容出现在 `wiki/INDEX.md` 和技能文件中，让 Agent 无需阅读源码即可获得更丰富的上下文。速度优先时使用 `--skip-deep` 仅运行结构化索引。

---

## 输出

### `wiki/INDEX.md`

代码库的顶层地图——每个 Wiki 页面覆盖哪些文件、每组的入口点、系统概述和关键请求流程（深度模式启用时）。

### `wiki/<group>.md`

每个逻辑文件夹集群一个页面。每个页面包含：

- **模块** — 覆盖的文件
- **关键符号** — 函数、类、方法及一行描述
- **关系** — 该组调用了什么、被什么调用、导入了什么
- **入口点** — 无调用者的符号（架构根节点）
- **数据流** — 穿过该模块的端到端流程 *(深度模式)*
- **设计约束** — 需要遵守的不变量和非显而易见的规则 *(深度模式)*

### `.indexer/skills/codebase.md`

教会任何 LLM Agent 如何导航你的代码库的技能文件：

- 代码库统计（符号数、文件数、索引日期、提交）
- 系统概述和关键请求流程
- Wiki 页面索引及入口点
- 每个模块提取的关键约束
- Agent 的分步导航工作流
- 组件 ID 格式参考和清单查找说明

### `.indexer/vector_db/`

ChromaDB 向量存储，包含每个索引符号的嵌入。REST API 和 MCP 服务器用于语义搜索。

---

## 加载技能文件

运行 `repo-wiki run` 后，技能文件位于 `.indexer/skills/codebase.md`。加载到你的 Agent 中一次——在任何代码库导航问题上自动激活。

### Claude Code

```bash
# 全局——在所有项目中可用
mkdir -p ~/.claude/skills/codebase
cp .indexer/skills/codebase.md ~/.claude/skills/codebase/SKILL.md

# 项目级——仅在此仓库中可用
mkdir -p .claude/skills/codebase
cp .indexer/skills/codebase.md .claude/skills/codebase/SKILL.md
```

### Cursor / Windsurf / Copilot / Zed

与 kiwiskil 相同——参见[原版说明](https://github.com/ximihoque/kiwiskil#loading-the-skill)。

---

## 配置

### `.indexer.toml`（每仓库，由 `repo-wiki init` 创建）

```toml
[llm]
provider = "openai/qwen-plus-2025-04-28"  # 任意 LiteLLM 兼容模型字符串
api_key_env = "DASHSCOPE_API_KEY"          # 环境变量名，非密钥本身
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

支持任何 LiteLLM 兼容的提供商：OpenAI、Anthropic、Gemini、Ollama、本地模型。

### `.env`（服务级，用于 REST API / MCP 模式）

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

# REST API 服务
REPO_WIKI_API_KEY=                     # API 认证密钥（设置后需 Bearer Token）
PUBLIC_DOMAIN=https://your-server.com  # 公开域名，用于 webhook URL 生成
WEBHOOK_SECRET=your-webhook-secret     # Webhook 签名验证密钥
```

---

## 支持的语言

| 语言 | 状态 | 解析器 |
|------|------|--------|
| Python | 已支持 | stdlib `ast` |
| JavaScript（`.js`、`.jsx`、`.mjs`、`.cjs`） | 已支持 | tree-sitter |
| TypeScript（`.ts`、`.tsx`） | 已支持 | tree-sitter |
| Go | 已支持 | tree-sitter-go |
| Rust（`.rs`） | 已支持 | tree-sitter-rust |
| Java（`.java`） | 已支持 | tree-sitter-java |
| Ruby（`.rb`） | 已支持 | tree-sitter-ruby |

---

## 设计原则

- **仅结构化事实** — Wiki 页面包含符号、关系和入口点。无散文摘要，无架构观点。客户端 LLM 自行得出结论。
- **提交而非服务** — Wiki 是仓库中的纯 Markdown。随代码一起，由 Git 追踪，人和 Agent 都可读。
- **默认增量** — Git diff + 内容哈希清单意味着每次提交仅重新处理变更文件。
- **提供商无关** — LiteLLM 意味着你可以使用任何模型，本地或云端，无需更改工具。
- **搜索就绪** — 向量嵌入和语义搜索是一等公民，不是附加功能。

---

## 许可证

MIT
