# RepositoryIndex 绿地版本发布检查

日期：2026-08-20

## 发布范围

- `RepositoryIndex` 成为唯一结构事实源。
- Git tree/blob 捕获、SQLite generation、Exact/FTS5/Graph 检索和可选 enrichment revision。
- CLI、REST、MCP、Wiki 与 Skill 投影全部切换到 generation interface。
- 删除 Manifest、JSON 搜索/关系状态、旧向量库、rebuild/migrate/rollback 及旧缓存实现。

## 发布前检查

- [x] `python3 -m pytest -q`：100/100 通过。
- [x] `python3 -m compileall -q indexer tests` 通过。
- [x] 管理页内联 JavaScript 语法检查通过。
- [x] `git diff --check` 通过。
- [x] 生产代码与当前文档无旧状态路径引用。
- [x] 质量基线 Recall@5、MRR@10、NDCG@10 均为 1.0。
- [x] 10/100/500/5000 文件性能基线已更新。
- [x] 5000 文件单文件增量只扫描和解析 1 个 blob；三次独立运行中位数 49.503 ms。
- [x] 5000 文件查询 P95 三次独立运行中位数 9.754 ms。
- [x] 多分支相同内容只保存一份 parse artifact，并复用 embedding。
- [x] parse/transaction/provider 失败不推进或破坏结构 branch head。
- [x] staged/worktree snapshot 不修改 checkout、真实 index 或 `.git/objects`。
- [x] generation/enrichment/synthetic Git object GC、任务恢复、SQLite integrity/foreign-key 检查通过。
- [x] 连续两次本地运行的第二次为 `unchanged`，Projection 不会自触发新 generation。

## 安装与初始化

这是无旧状态兼容层的绿地版本，不执行 Manifest 或向量目录迁移。

1. 停止旧的索引写任务。
2. 备份或直接移除旧 `.indexer/cache/`、`.indexer/vector_db/`、`.indexer/manifest.json` 与旧分支 worktree 目录。
3. 安装新版本并运行 `repo-wiki init`。
4. 运行 `repo-wiki run` 发布结构 generation 与 Wiki/Skill 投影。
5. 如需要 dense 检索，配置 embedding 后运行 `repo-wiki run --enrich`。
6. 运行 `repo-wiki maintain`，确认输出 `SQLite integrity: ok`。
7. 启动 REST/MCP 进程并执行 `/health`、`/repos`、`/api/validate/{name}`、`/search` 冒烟检查。

## 冒烟检查

- 单仓库 Exact 符号 ID 搜索首位命中目标。
- 自然语言查询返回 `matches`，调用关系只出现在 `related`。
- `preferred` 在 dense 未就绪时返回 local 结果及 degradation。
- `required` 在 dense 未就绪时返回 `HYBRID_REQUIRED_UNAVAILABLE`。
- 多分支请求缺少 branch 时返回 400；指定 branch 后 generation 与结果 scope 一致。
- 远端 ref 前进但本地分支未 checkout 时，sync 使用新的 `origin/<branch>` tree。
- 删除和重命名文件后无残留符号或 embedding 映射。

## 运行与发布影响

- 无外部数据库 SQL；本地新状态为 `.indexer/state/repository-index.sqlite3` 与 `.indexer/state/git-objects`。
- REST/MCP 进程必须重启以加载新路由和 generation 契约。
- 旧 `/rebuild`、`/rebuild-all`、旧 CLI 强制/迁移/回滚参数已移除，调用方需改用 `/sync`、`/sync-all` 或 `repo-wiki run`。
- Dense enrichment 改为显式选择：CLI 使用 `--enrich`，REST 请求使用 `"enrich": true`。
- 本次工作区未执行 commit、push 或部署；这些仍是独立发布动作。
