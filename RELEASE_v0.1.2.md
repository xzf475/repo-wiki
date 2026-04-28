# v0.1.2 (2026-04-28)

## 主要更新

### 🚀 MCP 服务器增强

- **MCP API 密钥认证** — 新增 `MCP_API_KEY` 配置，支持 Bearer Token 认证，保护 MCP 端点安全
- **Streamable-HTTP 模式修复** — 修复 `host`/`port` 参数传递问题，远程 MCP 服务器可正常绑定指定地址
- **DNS 反绑定保护** — MCP SDK 1.27 内置的 Host 头校验问题已解决，外部 IP 可正常连接（不再返回 421）
- **HTTP Host 头兼容** — 处理了 uvicorn/Starlette 层的 HostHeaderMiddleware 拦截问题，兼容外部域名访问

### 📦 Docker 部署改进

- 新增 `docker-entrypoint.sh` — 支持同时启动 REST API 和 MCP 服务器
- 新增 `HEALTHCHECK` 指令 — 容器健康状态可自动检测
- .env 配置新增 `MCP_ENABLED`、`MCP_PORT`、`MCP_API_KEY`
- 容器构建优化 — 更快的增量构建

### 📋 仓库管理与搜索

- **默认分支自动检测** — 注册仓库时如未指定分支，自动检测 `main`/`master` 等默认分支
- **仓库列表增强** — 显示 `last_indexed_commit`、`branches`、`has_vector_db` 等信息
- **搜索优化** — 单分支搜索结果过滤修复（单分支时不再加 branch 过滤条件，兼容旧索引数据）
- **日志增强** — 重建、同步、注册任务添加详细日志

### 🔧 代码质量与重构

- 集中 `git` 模块导入，提高代码可维护性
- 重构 MCP 服务器认证逻辑，代码结构更清晰
- 新增 v0.1.1 到 v0.1.2 共 14 个 commits

### 📝 文档与技能

- 新增 `skills/SKILL.md` — repo-wiki MCP Agent 技能，指导 AI 使用 MCP 工具进行代码分析
- 新增 `.indexer/skills/codebase.md` — 代码库导航技能文件
- 新增 `.indexer.toml` 配置文件
- 更新 README/README_EN — MCP 工具表、认证说明、技能安装指南
- 新增 `wiki/tests_fixtures.md` 等测试文档

---

## 详细变更

```
3a9bfc3 feat(mcp): 添加 MCP 工具文档和代码分析技能
b4112fc fix(mcp_server): 修复MCP认证并禁用DNS重绑定保护
19dfa17 refactor(mcp_server): 移除TrustedHostMiddleware并重构主机验证逻辑
8ff9a71 refactor(cli): 添加os模块导入以支持路径操作
50ff6f3 fix: 移除多余的分支条件判断
b7afe16 docs: 更新README和文档内容
5ead16e refactor(mcp_server): 重命名变量和方法以更准确表达意图
e2e10a8 fix(mcp_server): 修复MCP认证逻辑并添加TrustedHostMiddleware
4f499f2 feat(mcp): 添加 MCP API 密钥认证支持
f03b37c fix(indexer): 修复streamable-http模式下服务器设置问题
466f4e0 refactor(rest_api): 集中导入git相关模块
4e676c1 feat: 添加MCP服务器支持并优化仓库显示
208e510 feat: 添加默认分支检测功能
468ac7f feat: 添加日志记录以跟踪重建、同步和注册任务的状态
```

## 文件变更

20 files changed, 1652 insertions(+), 166 deletions(-)

### 新增文件
- `docker-entrypoint.sh` — Docker 入口脚本，支持多服务启动
- `.indexer.toml` — 仓库索引配置
- `.indexer/skills/codebase.md` — 代码库技能文件
- `skills/SKILL.md` — MCP Agent 技能
- `skills/evals/evals.json` — 技能测试用例

### 修改文件
- `indexer/cli.py` — 修复 serve 命令参数传递
- `indexer/mcp_server.py` — MCP 认证、Host 头兼容、DNS 反绑定修复
- `indexer/rest_api.py` — 集中 git 导入、分支检测、日志增强
- `Dockerfile` — 增加 HEALTHCHECK
- `docker-compose.yml` — 增加 MCP 环境变量
- `README.md` / `README_EN.md` — 全面更新文档
- `.env.example` — 增加 MCP 配置项
