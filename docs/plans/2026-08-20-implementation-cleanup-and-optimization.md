# 实现清理与性能优化迭代计划

> 已被 `2026-08-20-greenfield-repository-index-plan.md` 取代。本文仅保留为旧实现的审查记录，不再作为当前架构说明。

日期：2026-08-20

## 结论

本轮“正确性与规范清理”阶段已完成。更新慢和检索不准并非单一算法问题，核心是四类状态没有统一：源码内容、关系闭包、本地制品、远程描述/向量。CLI、Hook、REST 和多分支注册又曾分别维护候选与修复逻辑，导致同一仓库出现不同完成度。

当前已收敛到 `IndexEngine` 与 `CodeSearch` 两个接口；剩余主要问题是规模复杂度，而不是已知的结果一致性缺陷。

## 根因与处理结果

| 根因 | 影响 | 本轮处理 |
|---|---|---|
| `local-only` 更新 Manifest，但跳过描述和向量 | 下一次在线增量误判无变化，向量永久缺失或删除残留 | Manifest v3 增加待远程补齐文件和待删除文件，在线成功后才清账 |
| 关系闭包重算后只写候选文件到搜索库 | 未修改调用者/被调者的 `called_by` 陈旧 | 搜索库更新范围改为完整 affected closure，并覆盖调用边新增/删除 |
| REST 自行修复 Wiki、Skill、向量目录 | CLI/REST 候选语义分叉，删除文件可能被提前返回 | 制品健康检查并入 `IndexEngine.plan`，REST 只做请求与进度适配 |
| rebuild 先删除旧 Wiki、缓存、向量和 Manifest | 新任务失败会丢失最后可用快照 | 取消预删除，Manifest 保持最后提交点；失败保留旧快照 |
| 初次多分支注册共享 checkout 和 Manifest | 后续分支可能跳过同名同内容符号 | 注册复用 `BranchIndexCoordinator` 和独立 worktree |
| 多分支搜索未要求 branch，按组件 ID 去重 | 相同组件跨分支随机折叠 | 多分支 REST/MCP 搜索要求显式 branch，结果和去重键携带 branch |
| Dense 服务异常直接终止混合检索 | 已算出的本地 BM25/精确结果也无法返回 | Dense 阶段可降级到本地候选；查询向量 LRU 加锁 |
| 向量迁移覆盖已存在的新 ID | 失败时可能把较新向量不可逆回退 | 已存在目标只校验不覆盖；新建目标失败时删除，旧行保留 |
| 迁移审计只检查文件存在 | 空 Wiki/Skill 也能误报覆盖完整 | 审计组件 ID 是否出现在 Wiki、Wiki 页面是否出现在 Skill |
| 历史修复测试大量断言源码字符串 | 重命名即失败，却不能证明用户行为 | 删除过期、重复和实现细节测试，以接口行为回归替代关键约束 |

## 本轮清理范围

- 删除无生产调用的 `_collect_affected_files`、`_rank_search_hits`、`_annotate_match_reasons`、`_get_type_name`、`load_existing_nodes`、`_is_indexable`。
- 删除多处未使用 import、REST 旧流水线参数、破坏性 rebuild 清理块和手工制品修复分支。
- 抽取 tree-sitter 通用 `_node_name`，替代 Go、Java、JavaScript/TypeScript、Ruby、Rust 五份重复实现。
- 删除已失效的 `hooks.deep` 配置和无效参数；预提交固定执行确定性本地模式。
- 将伪造错误排名的“向量基线”改为同一受控 Dense provider 的真实 dense-only 输出，并明确它不是生产语料基准。
- 为增量补向量、删除向量、关系边变化、重建失败、多分支注册/搜索、Dense 故障和迁移冲突增加行为测试。

## 阶段状态

### C1：正确性与规范清理

状态：已完成

退出条件：

- 本地预提交后，在线增量仍能发现待补描述/向量和待删向量。
- 关系边新增或删除后，搜索关系元数据同步更新。
- rebuild 失败不删除最后可用 Manifest 与 Wiki。
- CLI、REST、Hook 的候选和制品修复统一经过 `IndexEngine`。
- 初次多分支注册使用隔离 worktree；多分支检索不能省略 branch。
- Dense 故障仍返回本地检索结果；迁移不覆盖已有新向量。
- 无引用私有定义和非刻意 re-export 的未使用 import 为 0。
- 全量测试、compileall、JSON 校验和 diff-check 通过。

### C2：更新复杂度优化

状态：待迭代

目标方案：

1. 将 `SearchCorpus` 从整文件 JSON 替换为 SQLite：普通字段建 B-tree，文本字段使用 FTS5，关系边独立表；单文件更新使用事务，不再 O(N) 重写。
2. 为索引快照保存可信的 Git tree/dirty checkpoint。干净工作树优先使用 Git 变更集合缩小哈希范围，最终仍用内容哈希确认，异常状态回退到全量校验。
3. 将分词、文档长度、DF 和 trigram 数据做成随 corpus generation 更新的持久化统计；查询从“每次扫描全库”降为倒排召回。
4. 给 REST 进程缓存按 repo/branch/generation 构建的 `CodeSearch`，generation 变化时精确失效。

退出条件：

- 5000 文件仓库无变化检查 P95 小于 300 ms。
- 单文件增量不读取或重写无关搜索记录，写放大不超过变更记录的 3 倍。
- 本地检索 P95 小于 100 ms，且查询过程不全表重新计算 DF。
- 10/100/500/5000 文件增长曲线、索引体积和峰值内存纳入 CI 基线。

### C3：快照事务与服务拆分

状态：待迭代

目标方案：

1. 将 `rest_api.py` 拆为路由校验、仓库应用服务、任务编排三个模块，注册/同步/重建共用一个 application service。
2. Wiki、关系、搜索和 Manifest 写入同一 generation 临时目录；全部完成后切换 generation 指针。向量记录携带 generation，失败 generation 可整体清理。
3. 迁移命令增加预检、冲突报告、dry-run、完整 generation 回滚和幂等重跑。

退出条件：

- 任一阶段注入失败后，读请求只能看到完整旧 generation 或完整新 generation。
- 注册、同步、重建不再包含重复 checkout、候选或状态提交代码。
- 迁移失败和中断均能恢复到逐字节一致的旧 Manifest 与语义一致的向量集合。

### C4：生产检索质量门槛

状态：待迭代

目标方案：

1. 从真实仓库建立带 branch、语言、查询意图和相关性等级的标注集。
2. 固化发布前版本的真实检索输出作为基线，不再用人工错误排名替代。
3. 在离线 Recall/MRR/nDCG 外增加无结果率、分支误命中率、关系陈旧率和在线延迟。

退出条件：

- 新版本在同一生产快照上 Recall@5、MRR@10、nDCG@10 均不低于旧版本。
- 分支误命中率和已知关系陈旧率为 0。
- Dense 不可用演练下，本地检索成功率为 100%。

## 推荐实施顺序

| 优先级 | 切片 | 预计工作量 | 收益 |
|---|---|---:|---|
| P0 | SQLite/FTS5 SearchCorpus + generation 迁移 | 3–5 天 | 消除更新整库重写和查询全库扫描 |
| P0 | Git checkpoint + 内容哈希确认 | 2–3 天 | 显著降低无变化和小增量扫描成本 |
| P1 | snapshot generation 原子切换 | 3–5 天 | 消除跨制品半成功状态 |
| P1 | REST application service 拆分 | 2–4 天 | 降低重复逻辑与后续修改风险 |
| P1 | 真实语料评测与发布门禁 | 2–3 天 | 让“检索更准”有可复现证据 |

每个切片仍按“行为测试 → 最小实现 → 目标测试 → 全量测试 → 基线更新”的顺序验收；未满足退出条件不得标记完成。
