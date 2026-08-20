# 索引更新与代码检索迭代计划

> 已被 `2026-08-20-greenfield-repository-index-plan.md` 取代。本文仅保留为旧实现的分析记录，不再作为发布或运维依据。

日期：2026-08-20

## 目标

把当前分散在 CLI、REST、Hook 和检索函数中的索引行为收敛为两个深模块：

- `IndexEngine.run(IndexRequest) -> IndexResult`：负责一致、可观测、端到端增量的索引更新。
- `CodeSearch.search(SearchRequest) -> SearchResponse`：负责精确匹配、词法召回、向量召回、重排和关联上下文。

迭代以“阶段退出条件全部满足”为完成标准，不以代码已提交或局部测试通过代替阶段完成。

## 基线问题

1. pre-commit 在提交前记录 commit，后续同步会重复调度已经按内容索引过的文件。
2. 单文件增量仍加载全仓缓存节点并重算完整调用图。
3. 描述和 Embedding 缓存签名不包含源码正文，行为变化可能继续复用旧向量。
4. 向量主键未包含分支，相同符号在不同分支会互相覆盖。
5. `search_symbols` 只有向量排序，精确命中只被解释但不重排；调用图扩展会突破 `top_k`。
6. 增量生成 Skill/INDEX 时使用本次候选数和符号数，不能代表完整快照。
7. 现有性能测试以源码结构断言为主，缺少真实的操作计数和检索质量门槛。

## 阶段 P0：索引正确性基线

状态：已完成

范围：

- 候选文件以内容哈希为最终依据；Git diff 仅作为发现提示，不能强制重复索引哈希未变的文件。
- 符号语义签名包含源码正文，使函数体变化必然失效描述和 Embedding 缓存。
- 向量存储 ID 包含分支，逻辑组件 ID 与存储 ID 分离。
- 精确组件 ID、符号名和路径命中参与确定性重排。
- `matches` 严格遵守 `top_k`；调用图扩展结果单独返回或至少不突破上限。
- Skill/INDEX 的文件数、符号数和页面目录来自应用增量后的完整 Manifest 快照。
- 修复 `status` 与 `agent diagnose` 对可索引文件范围不一致的问题。

退出条件：

- Manifest 哈希无变化时，同步候选为 0，即使 HEAD 与记录 commit 不同。
- 同行数、同调用关系但函数体行为变化时，描述签名和 Embedding 签名都会变化。
- 同一组件可同时存在于 `main` 和 `feature`，删除或更新一个分支不影响另一个分支。
- 精确组件 ID 在候选集中必须排第一。
- `top_k=1` 时匹配结果始终只有一条。
- 增量后生成的完整文件数和唯一符号数与 Manifest 一致。
- CLI status 与 agent diagnose 的 stale 文件集合一致。
- P0 新增回归测试和全量测试通过。

完成证据：

- CLI 与 REST 均通过 `select_index_candidates` 以 Manifest 内容哈希判定候选；commit 差异只作为状态信息。
- `ASTNode.source` 进入描述签名、描述输入和 Embedding 签名，长函数中部变化也会使缓存失效。
- 向量存储使用 `branch + component_id` 的存储主键，并保留逻辑组件 ID；分支级更新、查询和删除互不影响。
- 搜索在调用图扩展后执行确定性重排与去重，并在最终返回前严格截断 `top_k`。
- 增量 Wiki 返回完整页面目录，Skill 的文件数和唯一符号数按应用增量后的完整快照计算。
- `status` 与 `agent diagnose` 共享同一 freshness 结果和可索引文件过滤规则。
- P0 回归测试 8/8 通过；全量测试 265/265 通过；Python compileall 与 `git diff --check` 通过。

## 阶段 P1：统一增量索引模块

状态：已完成

范围：

- 新增 `IndexEngine` interface，CLI、REST、Hook 只保留适配逻辑。
- 建立 `IndexRequest`、`IndexPlan`、`IndexResult`，返回候选、影响范围、缓存命中、远程调用和阶段耗时。
- 持久化按文件组织的符号与调用关系，只更新变更文件及其关系闭包。
- tracked artifact 使用临时文件和原子替换，Manifest 最后提交。
- pre-commit 默认只执行确定性的本地阶段；深度 LLM 分析与提交信息生成移出关键路径。

退出条件：

- CLI、REST、Hook 的候选与结果对同一快照完全一致。
- 单文件修改不再加载全仓节点；处理规模与变更及影响闭包相关。
- 无变化更新的解析、LLM、Embedding、Wiki 写入计数均为 0。
- 失败任务不推进 Manifest 快照。
- 旧的调用链结构测试由 `IndexEngine` interface 行为测试替代。

完成证据：

- 新增 `IndexEngine.run(IndexRequest) -> IndexResult`，CLI、REST、Hook 均通过该 interface 执行。
- `RelationState` 持久化按文件关系摘要，单文件变更只加载关系闭包内的 AST 缓存。
- `IndexResult.metrics` 返回解析、缓存、LLM、Embedding、Wiki 写入和阶段耗时。
- 无变化 interface 测试证明解析、LLM、Embedding、Wiki 写入均为 0，且 Manifest 字节不变。
- 制品写入失败和向量更新失败测试均证明 Manifest 不会提前推进。
- pre-commit 固定为 `--staged --local-only --skip-deep`，远程调用退出提交关键路径。
- Manifest v3 显式记录待补远程文件和待删向量；本地预检推进内容快照时不会吞掉后续在线工作。
- Wiki/Skill/搜索/向量健康检查统一进入 `IndexEngine.plan`；REST 删除了第二套候选和制品修复逻辑。
- P1 interface 与补强回归通过；当前全量测试 255/255 通过；compileall 与 diff-check 通过。

## 阶段 P2：混合检索与质量门槛

状态：已完成

范围：

- 新增 `CodeSearch` interface。
- 索引签名、文档、源码正文和长符号分块。
- 建立组件 ID/路径/符号名的精确索引与中英文 trigram/BM25 词法索引。
- 合并词法与 Dense 候选，使用 RRF 和结构化特征重排。
- `matches` 与 `related` 分离，结果包含稳定的 score breakdown。
- 建立中英文、组件 ID、路径、行为语义和入口点查询集。

退出条件：

- Recall@5、MRR@10、nDCG@10 均达到评测集门槛并高于 P0 基线。
- 精确 ID 和路径查询不依赖远程 Embedding 即可返回。
- 冷查询只调用一次 Embedding；归一化相同的缓存查询不重复调用。
- 任何匹配结果都包含可解释且可比较的排序分数。

完成证据：

- 新增 `CodeSearch.search(SearchRequest) -> SearchResponse`，REST、MCP 与兼容检索入口均通过该 interface。
- `SearchCorpus` 按分支持久化组件 ID、路径、符号、源码签名和重叠长源码分块。
- 本地精确索引、中文/英文 BM25 与 trigram、Dense 候选通过 RRF 和结构特征统一重排。
- `matches` 与 `related` 分离，所有匹配都返回稳定的 `score_breakdown`。
- 精确组件 ID 和路径测试证明 Embedding 调用为 0；普通冷查询调用 1 次，归一化缓存查询调用 0 次。
- 五类确定性评测集的 Recall@5/MRR@10/nDCG@10 为 1.0/1.0/1.0，均高于同一受控 Dense provider 的 dense-only 基线 0.2/0.2/0.2；该数据是 interface 基线，不冒充生产语料评测。记录见 `docs/plans/2026-08-20-search-quality-baseline.json`。
- P2 interface 测试 5/5 通过；全量测试 276/276 通过；compileall 与 diff-check 通过。

## 阶段 P3：多分支规模化与发布验证

状态：已完成

范围：

- 使用分支 tree/content fingerprint 跳过无变化分支。
- 使用受控并发和独立 managed worktree 处理多分支，避免共享 checkout 互斥。
- 建立不同仓库规模下的更新操作计数、耗时和索引体积基线。
- 完成旧 Manifest/向量数据迁移、回滚和兼容验证。

退出条件：

- 多分支索引可并发且相互隔离。
- 相同内容的无变化分支不会产生解析或远程调用。
- 迁移前后检索结果和 Wiki/Skill 覆盖不丢失。
- 完整测试、性能基线、迁移演练和发布检查通过。

完成证据：

- `BranchIndexCoordinator` 使用 branch tree fingerprint、最多 2 个独立 detached worktree 并发执行，并只在分支成功后推进持久化指纹；失败分支下一轮会重试。
- REST 全分支同步/重建和初次多分支注册均接入协调器，不再轮流切换共享 checkout；共享 `SearchCorpus` 使用 reload-update-save 路径锁，向量集合写入按存储路径与集合名串行化。
- 相同分支 tree 第二次执行直接跳过；测试证明不会再次调用 worker，因此解析和远程调用均为 0。
- Manifest schema v1→v3 会保存精确字节备份、去重组件 ID 并初始化远程待办状态；搜索索引可由 AST 缓存重建；向量迁移不覆盖已存在的新 ID，新行校验成功后才删除旧行。
- 迁移覆盖审计核对 Manifest/搜索组件集合、组件 ID 在 Wiki 中的实际出现以及 Wiki 页面在 Skill 中的实际引用；`repo-wiki migrate` 和 `repo-wiki rollback-manifest` 提供迁移与回滚入口。
- 10/100/500 文件基线中，单文件增量始终只解析 1 个文件、加载 0 个无关缓存文件、产生 0 次远程调用；无变化运行的解析和 Wiki 写入均为 0。记录见 `docs/plans/2026-08-20-index-performance-baseline.json`。
- P3 interface/迁移/性能及复核回归通过；当前全量测试 255/255 通过；compileall、JSON 校验与 diff-check 通过；发布清单见 `docs/plans/2026-08-20-release-checklist.md`。

## 阶段 C1：实现复核、清理与稳定性补强

状态：已完成

完成内容：

- 修复关系闭包只更新候选搜索记录、local-only 吞掉远程工作、removed-only REST 同步提前返回等一致性问题。
- rebuild 不再预删除最后可用快照；多分支搜索要求显式 branch，Dense 故障保留本地结果。
- 删除无调用代码、重复 parser helper、失效 hook 配置、旧 REST 修复流水线以及过期/重复/源码结构测试。
- 将关键约束替换为 interface 行为回归，并为性能测试增加耗时与状态体积预算。

后续 C2–C4 的规模优化、快照事务与真实生产语料质量门槛见 `docs/plans/2026-08-20-implementation-cleanup-and-optimization.md`。

## 每轮迭代工作流

1. 从当前阶段选择一个最小但可验收的纵向切片。
2. 先写能够捕获该问题的 interface 行为测试。
3. 实现最小改动，保持旧调用方兼容。
4. 运行目标测试、相关模块测试和全量测试。
5. 更新本文档中的阶段状态、验证证据和未完成项。
6. 只有全部退出条件满足时，才把阶段标记为完成并进入下一阶段。

## 验证记录

| 日期 | 阶段 | 结果 | 证据 |
|---|---|---|---|
| 2026-08-20 | P0 | 已完成 | P0 回归 8/8；全量测试 265/265；compileall 与 diff-check 通过 |
| 2026-08-20 | P1 | 已完成 | interface 回归 6/6；全量测试 271/271；compileall 与 diff-check 通过 |
| 2026-08-20 | P2 | 已完成 | 检索回归 5/5；质量指标 1.0/1.0/1.0；全量测试 276/276 |
| 2026-08-20 | P3 | 已完成 | P3 回归 10/10；10/100/500 文件性能基线；迁移/回滚演练；全量测试 286/286；发布检查通过 |
| 2026-08-20 | C1 复核 | 已完成 | 关键一致性补强、无用代码和测试清理；全量测试 255/255；compileall、JSON 与 diff-check 通过 |
