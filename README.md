# repo-wiki

**让代码 Agent 基于同一份、可验证的仓库索引工作。**

repo-wiki 从不可变 Git tree 构建结构索引，提供精确符号匹配、FTS5 全文检索、调用图扩展和可选的 dense 增强，并生成 Wiki 与 Agent skill。CLI、REST 和 MCP 都通过同一个 `RepositoryIndex` module，返回相同 generation 下的结果。

[English](README_EN.md)

## 架构

```text
Git tree / staged / worktree snapshot
                 │
                 ▼
content-addressed parse artifacts
        │                    │
        ▼                    ▼
symbols / docs / FTS5   snapshot base + path overlay
        │                    │
        └─────────┬──────────┘
                  ▼
       generation + branch head ──► Wiki / Skill projection
                  │
        ┌─────────┼──────────┐
        ▼         ▼          ▼
      Exact      FTS5    lazy call graph
        └─────────┼──────────┘
                 ▼
            ranked matches
                 │
     shared optional embedding revision
```

核心约束：

- 输入是 Git tree，而不是可变 checkout；`@staged` 与 `@worktree` 也会先物化为确定性 tree。
- 分支头只在完整事务成功后切换；解析或写入失败不会破坏最后可用 generation。
- 解析制品、符号、检索文档、FTS 行与 embedding 按内容寻址，可跨分支复用；查询时才与分支路径组合。
- 相同 tree 直接复用同一个 snapshot；相近分支只保存相对基准 snapshot 的变更/删除路径，overlay 链达到深度上限时选择更小的全量或增量 checkpoint，普通增量不会重写全量路径。
- 调用关系只在主检索有命中且请求 related 结果时按 snapshot 惰性构建；导入路径用于消解同名符号，避免全局同名调用形成笛卡尔积。
- 本地检索始终可用；dense 增强失败时 `preferred` 降级，`required` 明确报错。
- 每个分支自动保留最近两代；全分支同步会删除不再匹配 Branch Rule 的索引 scope，并回收不可达 snapshot、解析制品、embedding 和 SQLite 空闲页。

同一仓库的所有分支共用 `.indexer/state/repository-index.sqlite3`，而不是每个分支创建一份数据库。数据库使用 SQLite WAL、外键与 FTS5；staged/worktree 合成 tree 的对象存储在 `.indexer/state/git-objects`，同步期间使用跨进程 lease 防止维护任务提前回收，不会修改 `.git`。可提交的投影是 `wiki/` 和 `.indexer/skills/codebase.md`。

Schema v4 是派生索引格式：从旧 schema 首次打开时会自动清理、压缩并重建空结构，不迁移旧索引行；高于当前版本的 schema 会被明确拒绝，避免旧程序破坏新格式。升级后运行一次 `repo-wiki run`（单仓库）或 `/sync-all`（托管多分支仓库）即可从 Git tree 恢复。

## 安装

要求 Python 3.11+ 与 Git。

```bash
pip install repo-wiki
```

从源码安装：

```bash
git clone https://github.com/xzf475/repo-wiki.git
cd repo-wiki
pip install -e .
```

## Docker

Docker Compose 默认启动 REST API 与 Web 控制台；MCP HTTP 服务可按需启用。首次启动先创建本地环境文件：

```bash
cp .env.example .env
# 仅使用结构索引和本地检索时，无需填写 embedding API key。
# 需要 dense enrichment 时，再在 .env 中配置对应 provider 的密钥。

docker compose up -d --build
docker compose ps
curl --fail http://localhost:7654/health
```

启动成功后访问：

- Web 控制台与 REST API：<http://localhost:7654>
- 健康检查：<http://localhost:7654/health>
- MCP：默认关闭；在 `.env` 中设置 `MCP_ENABLED=true` 后监听 `8000` 端口

主要 Docker 环境变量：

| 变量 | 默认值 | 用途 |
|---|---:|---|
| `API_PORT` | `7654` | REST API 与 Web 控制台端口 |
| `REPO_WIKI_API_KEY` | 空 | REST Bearer 认证；为空时不启用认证 |
| `MCP_ENABLED` | `false` | 是否同时启动 streamable HTTP MCP |
| `MCP_PORT` | `8000` | MCP 监听端口 |
| `MCP_API_KEY` | 空 | MCP Bearer 认证 |
| `PUBLIC_DOMAIN` | 空 | 生成 Webhook URL 时使用的外部域名 |
| `WEBHOOK_SECRET` | 空 | GitHub/GitLab Webhook 签名校验 |
| `EMBEDDING_*` | 见 `.env.example` | 可选 dense enrichment provider 配置 |

Compose 使用具名卷保存容器数据：

| 卷 | 容器路径 | 内容 |
|---|---|---|
| `repo_wiki_repos` | `/tmp/repo_wiki_repos` | 托管仓库、注册表、各仓库索引与 Wiki 投影 |
| `repo_wiki_data` | `/app/.indexer` | 服务工作目录下的索引状态 |
| `repo_wiki_wiki` | `/app/wiki` | 服务工作目录下的 Wiki 投影 |

常用运维命令：

```bash
docker compose logs -f repo-wiki
docker compose restart repo-wiki
docker compose up -d --build     # 更新代码或镜像后重建
docker compose down              # 停止容器，保留具名卷
```

`docker compose down -v` 会删除上述具名卷及其中的托管仓库和索引数据，请仅在确认需要清空数据时使用。

## CLI

```bash
repo-wiki init
repo-wiki run                 # 结构 generation + 投影
repo-wiki run --enrich        # 发布结构 generation 后执行 dense 增强
repo-wiki run --staged
repo-wiki status
repo-wiki maintain            # 恢复过期任务、GC、回收 SQLite 空闲页并检查完整性
```

`repo-wiki init` 安装的 pre-commit hook 使用 `repo-wiki run --staged`。它会一次性发布暂存 tree 的完整结构 generation，不会调用远程 provider。

Agent 辅助命令：

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

注册并建立结构索引：

```bash
curl -X POST http://localhost:7654/register \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://github.com/org/repo.git","branch":"main","enrich":false}'
```

检索：

```bash
curl -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"认证中间件","repo":"repo","branch":"main","top_k":10,"retrieval":"preferred"}'
```

多分支仓库必须显式传 `branch`。检索响应包含 `generation`、`tree_id`、`retrieval`、`degradations`，并把直接命中放在 `matches`、调用图扩展放在 `related`。

主要仓库接口：

| 路径 | 方法 | 用途 |
|---|---|---|
| `/register` | POST | 克隆、注册并同步仓库 |
| `/unregister` | POST | 从注册表移除；不删除仓库文件 |
| `/sync` | POST | 同步指定分支，未注册分支会加入注册表 |
| `/sync-all` | POST | 顺序同步所有分支，不切换 checkout |
| `/search` | POST | Exact + FTS5 + Graph，可选 dense |
| `/trace` | POST | 上游或下游调用链 |
| `/index-status` | POST | generation、tree 与新鲜度 |
| `/api/validate/{name}` | GET | 投影、generation、SQLite 完整性检查 |
| `/repos` | GET | 已注册仓库及各分支 generation |
| `/health` | GET | 服务存活状态 |

完整请求字段与 Agent 接口见 [API Reference](docs/api-reference.md) 和 [Agent Integration](docs/agent-integration.md)。Web 控制台位于服务根路径。

## MCP

单仓库 stdio：

```bash
cd /path/to/repo
repo-wiki serve
```

多仓库模式连接 REST：

```bash
repo-wiki serve --api http://localhost:7654
```

核心工具包括 `search_symbols_tool`、`trace_call_tool`、`get_source_context_tool`、`resolve_symbol_tool`、`impact_analysis_tool`、`change_plan_tool` 和 `get_index_status_tool`。搜索支持 `local`、`preferred`、`required` 三种 retrieval 模式。

## 配置

`.indexer.toml`：

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

Embedding 是可选 enrichment。未配置或服务不可用时，结构 generation、Wiki、Exact/FTS5/Graph 检索仍可使用。

REST 可通过 `REPO_WIKI_API_KEY` 开启 Bearer 认证；Webhook 可通过 `WEBHOOK_SECRET` 校验签名。

## 支持语言

Python、JavaScript、TypeScript、Go、Rust、Java、Ruby，以及通用文本回退解析。

## 验证

```bash
python -m pytest -q
python -m indexer.repository_benchmarks
```

当前性能与质量基线保存在 [docs/plans/2026-08-20-repository-index-baseline.json](docs/plans/2026-08-20-repository-index-baseline.json)。

## 许可证

MIT
