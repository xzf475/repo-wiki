# repo-wiki

**让任何 LLM 理解你的代码库。**

从任意仓库生成可提交的 Wiki、技能文件和向量检索——无需上云，无厂商锁定。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://pypi.org/project/repo-wiki/)
[![Forked from kiwiskil](https://img.shields.io/badge/forked%20from-kiwiskil-6366f1)](https://github.com/ximihoque/kiwiskil)

[安装](#安装) · [快速开始](#快速开始) · [与 kiwiskil 的区别](#与-kiwiskil-的区别) · [REST API](#rest-api) · [CLI](#cli) · [配置](#配置)

---

repo-wiki 从任意代码库生成可提交的结构化 Wiki、技能文件和向量检索索引。它让 LLM Agent 无需阅读源码即可导航代码——使用从你的仓库构建并提交到 Git 的知识图谱。

> **Fork 自 [kiwiskil](https://github.com/ximihoque/kiwiskil)** — repo-wiki 在原版基础上增加了 REST API、向量检索、查询改写、仓库健康检查和 Go 语言支持。

---

## 与 kiwiskil 的区别

repo-wiki 基于 kiwiskil 的核心索引引擎构建，额外增加了以下能力：

### REST API + Web 管理界面

通过 `repo-wiki serve-api` 启动完整的 REST API 服务，支持远程仓库管理：

- **注册仓库** — 通过 URL 克隆并索引，支持 GitHub PAT、GitLab Token、密码认证
- **同步 / 重建** — 带实时进度追踪的增量同步和全量重建
- **语义搜索** — 跨仓库向量相似度检索
- **调用链追踪** — 沿调用链向上或向下追踪
- **源码上下文** — 获取任意文件的指定行范围
- **Web 仪表盘** — 浏览器中管理仓库、浏览 Wiki、搜索符号

### 向量检索（RAG 就绪）

- **ChromaDB** 存储每个索引符号的向量嵌入
- **语义搜索** — 按向量距离排序返回结果，而非文本匹配
- **查询改写** — LLM 将自然语言查询扩展为多个精确检索词，提升召回率
  - 例：`"怎么处理认证"` → `["认证处理", "Authentication handler", "token verification", ...]`
- **调用图扩展** — 自动包含调用链上的相关符号

### 仓库健康检查与自动修复

- **校验端点** 检查：配置文件、清单文件、Wiki 页面、技能文件、向量库、过期文件
- **同步时自动修复**：缺失的 Wiki 页面、向量库、过期索引条目均可检测并修复
- **清单路径修正**：自动修正 manifest 中 Wiki 页面路径与实际文件名不一致的问题

### Go 语言支持

- 通过 tree-sitter-go 实现 Go 语言的 AST 解析——提取函数、方法、类型、接口和调用关系

### 异步任务处理

- 仓库注册、同步、重建均作为后台任务运行
- 实时进度更新（步骤名称 + 百分比），通过轮询获取
- 非阻塞——API 立即返回任务 ID

---

## 工作原理

1. **AST 解析** — 从源文件提取符号、导入和调用图（确定性，免费）
2. **LiteLLM** — 使用你配置的任意模型为每个符号生成一行描述
3. **密度分组器** — 按逻辑密度（而非目录结构）将文件组织为 Wiki 页面
4. **Embedding** — 通过配置的嵌入模型为每个符号生成向量表示
5. **ChromaDB** — 存储和索引向量，支持快速语义搜索
6. **Pre-commit Hook** — 保持 Wiki 同步，每次提交自动更新 Wiki 页面
7. **技能文件** — 生成在 `.indexer/skills/codebase.md`，让任何 LLM Agent 能通过结构化工具导航你的代码库

Wiki 是纯 Markdown，提交到你的仓库。无需云服务，无厂商锁定。

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

# 注册仓库（克隆 + 索引）
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/org/repo.git"}'

# 跨仓库搜索
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "认证中间件", "top_k": 10}'

# 打开 Web 仪表盘
open http://localhost:7654
```

---

## REST API

### 仓库管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/repos` | GET | 列出所有已注册仓库 |
| `/register` | POST | 通过 URL 注册并索引仓库 |
| `/sync` | POST | 同步仓库（拉取 + 重新索引变更） |
| `/rebuild` | POST | 全量重建（删除 + 重新索引） |
| `/unregister` | POST | 移除仓库 |
| `/api/validate/{name}` | GET | 仓库健康检查 |
| `/api/task/{task_id}` | GET | 轮询异步任务进度 |

### 搜索与导航

| 端点 | 方法 | 说明 |
|------|------|------|
| `/search` | POST | 语义搜索（含查询改写） |
| `/trace` | POST | 追踪调用链（向上/向下） |
| `/source` | POST | 获取文件指定行范围的源码 |
| `/api/repo/{name}` | GET | 仓库详情（Wiki 页面、清单） |

### 查询改写搜索

搜索默认调用 LLM 将查询扩展为多个精确检索词以提升召回率。可通过 `"rewrite": false` 关闭：

```json
{
  "query": "怎么处理认证",
  "repo": "my-project",
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
  "rewritten_queries": ["怎么处理认证", "认证处理", "Authentication handler", "token verification", "login authentication"]
}
```

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
repo-wiki serve-api         # 启动 REST API 服务和 Web 仪表盘
repo-wiki mcp               # 启动 MCP 服务器用于语义代码搜索
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

教会任何 LLM Agent 如何导航你的代码库的技能文件，包含：

- 代码库统计（符号数、文件数、索引日期、提交）
- 系统概述和关键请求流程
- Wiki 页面索引及入口点
- 每个模块提取的关键约束
- Agent 的分步导航工作流
- 组件 ID 格式参考和清单查找说明

### `.indexer/vector_db/`

ChromaDB 向量存储，包含每个索引符号的嵌入。REST API 用于语义搜索。

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

### `.env`（服务级，用于 REST API 模式）

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
```

---

## 支持的语言

| 语言 | 状态 | 解析器 |
|------|------|--------|
| Python | 已支持 | stdlib `ast` |
| JavaScript（`.js`、`.jsx`、`.mjs`、`.cjs`） | 已支持 | tree-sitter |
| TypeScript（`.ts`、`.tsx`） | 已支持 | tree-sitter |
| Go | 已支持 | tree-sitter-go |
| Rust、Java、Ruby | 计划中 | tree-sitter |

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
