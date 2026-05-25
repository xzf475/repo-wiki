# Changelog

## 0.3.3 - 2026-05-23

- Added Agent-focused local and remote workflows: edit context, symbol resolution, impact analysis, change planning, post-edit verification, change sets, coverage mapping, index diff reports, stable symbol IDs, entry point discovery, cross-repo graphs, and capability manifests.
- Added `repo-wiki agent` CLI commands for local Agent context, planning, verification, diagnostics, capabilities, and schema export.
- Added REST/MCP Agent contracts, including `/agent-capabilities`, `/agent-schema`, and machine-readable JSON schemas.
- Hardened manual reindex and rebuild flows so branch checkout/reindex tasks clean worktrees consistently and surface final task errors to the UI.
- Split Agent implementation boundaries into `agent_context`, `agent_diff`, `agent_graph`, `agent_diagnostics`, `agent_protocol`, and `agent_contracts` while keeping `indexer.retrieval` compatibility wrappers.
