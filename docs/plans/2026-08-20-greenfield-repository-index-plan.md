# RepositoryIndex 绿地替换迭代计划

## 决策

不再继续扩展 Manifest、SearchCorpus JSON、RelationState JSON、分支 worktree 和跨制品修复逻辑。新实现以 `RepositoryIndex` 作为唯一业务 module，以 SQLite 中原子发布的 generation 作为唯一结构事实源。

旧实现仅用于行为和质量对照；新实现完成切换后直接删除，不提供旧状态迁移。

## 外部 interface

```python
sync(SyncRequest) -> SyncReport
search(SearchRequest) -> SearchResult
inspect(IndexScope) -> IndexStatus
enrich(IndexScope) -> EnrichmentReport
symbols/files/trace(IndexScope, ...) -> structural projections
integrity() -> IntegrityReport
maintain() -> MaintenanceReport
```

CLI、REST、MCP 只负责协议转换。调用方不得传入候选文件、缓存目录、向量集合、`force`、`skip_deep` 等 implementation 细节。

## 核心不变量

1. 每次同步先将来源固化为不可变 `tree_id`；后续阶段不得读取变化中的 ref。
2. `repo + branch` 必须显式存在，不允许空分支表示跨分支搜索。
3. 文件映射、符号、关系、Exact/FTS 投影和 branch head 在同一个 SQLite 事务中发布。
4. 读请求只能看到完整旧 generation 或完整新 generation。
5. AST 解析产物按 `blob_id + parser_version + context_hash` 内容寻址，可跨分支复用。
6. 无变化 tree 同步不得解析文件、写结构索引或调用远程 provider。
7. Embedding/LLM 属于 enrichment revision；失败不得阻塞结构 generation。
8. Dense 不可用时，preferred 模式返回本地结果和显式 degradation；required 模式返回类型化错误。
9. 直接命中进入 `matches`，关系扩展只进入 `related`。
10. Wiki、Skill 和报告均为可重建 projection，不参与同步规划和提交正确性。

## 状态模型

- `repositories`：仓库身份。
- `generations`：`repo/branch/tree_id/parent` 与增量统计。
- `branch_heads`：当前可见 generation 指针。
- `parse_artifacts`：版本化 AST 解析结果。
- `files`：当前 branch head 的 `path -> blob/artifact` 物化映射。
- `symbols` / `relations`：当前 branch head 的符号与调用边物化视图。
- `documents` / `documents_fts`：事务性本地检索投影。
- `embeddings`：按内容签名与模型版本复用。
- `enrichment_revisions` / `jobs`：异步 enrichment 可见性与幂等任务。
- `.indexer/state/git-objects`：staged/worktree 合成 tree 的持久内容对象，不修改 `.git`。

## 阶段状态

### R0：契约与质量基线

状态：已完成

范围：

- 固化 `sync/search/inspect` 类型和类型化错误。
- 用临时 Git 仓库建立 interface 行为测试。
- 建立准确率、延迟、写放大和多分支复用基线。

退出条件：

- 原子发布、无变化、删除、分支隔离、失败回滚均有黑盒测试。
- 质量集使用真实查询与期望符号，不使用手工伪造的错误排名。

完成证据：

- 28 个 `RepositoryIndex` 黑盒测试覆盖首次发布、无变化、增删改、重命名、跨分支复用、分支隔离、快照隔离、GC/恢复、语法失败、事务失败、Exact/FTS/Graph 和真实语料质量门槛。
- 质量集直接创建真实 Git 仓库，并在同一语料上对比旧本地检索；Recall@5、MRR@10、NDCG@10 均为 1.0，且不低于旧实现。

### R1：内容寻址结构 generation

状态：已完成

范围：

- 直接读取 Git tree/blob，取消新内核对长期 worktree 的依赖。
- 使用 SQLite WAL、外键和短写事务。
- 解析唯一新 blob，按受影响闭包更新符号与关系。
- 原子切换 branch head。

退出条件：

- 无变化 tree 除 ref 解析外为 `O(1)`。
- 单文件变化不读取或重写无关 parse artifact。
- 任意失败均不推进 branch head。
- 相同 blob 跨分支只解析一次。

完成证据：

- `GitSnapshot` 使用 tree/blob OID、`diff-tree`、`ls-tree` 和 `cat-file --batch`，不创建 worktree。
- `RepositoryStore` 使用 SQLite WAL、外键、FTS5 触发器和短事务；branch head 与结构投影原子提交。
- 解析产物按 `blob_id + parser_version + context_hash` 保存；跨分支相同 tree 的第二次同步解析数为 0。
- 5000 文件三次独立运行中位数中，单文件增量只扫描并解析 1 个文件，耗时 49.503 ms；无变化耗时 11.978 ms。

### R2：本地混合检索

状态：已完成

范围：

- Exact/path/symbol 索引、FTS5 和有界图扩展。
- 各召回器独立取候选，使用 RRF 融合和确定性结构重排。
- 返回 score breakdown、generation 和 freshness。

退出条件：

- 查询不扫描全库重算 DF。
- `matches` 与 `related` 严格分离。
- 5000 文件本地查询 P95 小于 100 ms。
- 质量集 Recall@5、MRR@10、NDCG@10 不低于旧实现，并记录真实差异样本。

完成证据：

- Exact 命中优先，FTS5 使用持久化倒排索引，调用关系按增量 raw-call facts 重建；查询不重算全库 DF。
- Exact 命中存在时不会被仅包含调用文本的词法候选污染，调用者进入 `related`。
- 5000 文件、30 次查询的本地 P95 三次独立运行中位数为 9.754 ms，低于 100 ms 门槛。
- 完整基线见 `docs/plans/2026-08-20-repository-index-baseline.json`。

### R3：异步 enrichment revision

状态：已完成

范围：

- 持久化幂等 job/outbox。
- Embedding 按内容签名缓存，完整 revision 原子可见。
- preferred/required/local 三种检索语义。

退出条件：

- Provider 故障不影响本地 generation 发布和检索。
- 不存在部分向量静默可见。
- 响应明确返回 dense coverage、revision 和 degradation。

完成证据：

- 结构 generation 在同一事务创建持久化 enrichment job；provider 执行位于事务外，失败只将 job 标记为 failed。
- 文档向量按内容签名与模型复用；跨分支相同内容不会重复调用 provider，单文件变化只补 1 个新签名。
- 当前 generation 的全部映射、LSH buckets、revision 和 enrichment head 在同一事务中发布，不存在部分向量可见。
- `local/preferred/required` 三种模式已有行为测试；query provider 故障时 preferred 返回本地结果和 degradation，required 返回类型化错误。
- enrichment 对同一 generation/model 幂等；provider/query 故障回归均通过。

### R4：Adapter 切换与旧实现删除

状态：已完成

范围：

- CLI、REST、MCP 全部调用 `RepositoryIndex`。
- Wiki/Skill 改为指定 generation 的 projection。
- 删除 Manifest/SearchCorpus/RelationState/BranchIndexCoordinator 及迁移修复路径。
- 删除只验证旧源码结构的字符串测试。

退出条件：

- 三类 adapter 对同一 scope 返回相同 generation 和排序。
- 生产代码不再读取旧状态文件。
- 删除旧模块后全量测试仍通过。

完成证据：

- CLI、REST、MCP 的搜索与状态均通过 `RepositoryService` 进入同一个 `RepositoryIndex` interface；adapter 回归验证 generation 与排序一致。
- 多分支 REST 搜索/调用链要求显式 branch；远端同步优先读取 `refs/remotes/origin/<branch>`，不会因本地分支未 checkout 而停留在旧 tree。
- 多分支同步只 fetch refs 并逐 tree 读取，投影明确选用配置中的首个分支。
- Manifest、JSON SearchCorpus/RelationState、旧向量库、重建/迁移/回滚路径及其结构耦合测试已删除；生产路径与当前文档无旧状态引用。
- 全量测试 100/100、Python compileall、前端脚本语法与 `git diff --check` 均通过。

### R5：规模验证与收口

状态：已完成

范围：

- 10/100/500/5000 文件和多分支重复 blob 基准。
- generation/enrichment GC、崩溃恢复和数据库一致性检查。
- 更新 README、Wiki、发布清单和运维诊断。

退出条件：

- 增量复杂度为 `O(changed blobs + affected closure)`。
- 多分支存储随唯一 blob 数增长，而不是随分支副本线性增长。
- 全量回归、性能门槛、质量门槛和数据库一致性检查全部通过。

完成证据：

- 10/100/500/5000 文件基线已重跑；5000 文件单文件增量中位数 49.503 ms、无变化 11.978 ms、查询 P95 9.754 ms。
- 自动发布只回收本次 delta 触达的孤儿 artifact/embedding，避免全库 GC 把增量重新退化为 `O(N)`；每分支自动保留最近两代。
- 显式 `repo-wiki maintain` 可恢复中断 enrichment、回收旧 generation/revision/artifact/embedding/synthetic Git object，并执行 SQLite 页完整性与外键检查。
- 两个相同分支副本产生 4 条 file 映射但仅 2 个 parse artifact，存储随唯一 blob 增长。
- staged/worktree snapshot 使用独立 index 与 `.indexer/state/git-objects`，不修改真实 index/checkout/`.git/objects`；连续运行第二次为 `unchanged`。
- Projection 会删除不再属于当前 generation 的旧 Wiki 页；README、中英文 API/Agent 文档、Skill、Wiki 与发布清单已更新。

## 实施原则

每个阶段严格执行：行为测试 → 最小实现 → 目标测试 → 全量回归 → 性能/质量证据 → 更新阶段状态。未满足退出条件不得标记完成。
