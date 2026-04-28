# Codebase Index

## System Overview

The system is a CLI-based indexer tool (indexer/cli.py) with subcommands for initialization, status monitoring, git hook management (install, remove), and a built-in API server (serve, serve_api). Its architecture likely comprises a CLI entry point that dispatches to internal modules for configuration, hook scripts, and a REST API to expose index data. The hook mechanism integrates with version control (e.g., Git pre-commit) to automatically update the index, while the serve module provides real-time query access. Overall, the tool maintains a local index file and coordinates between CLI commands, hook triggers, and an HTTP API.
## Key Flows
- init -> config creation -> hook installation (hook_install) -> index setup
- git pre-commit hook triggered -> hook module -> index update -> status check
- serve -> API server start -> index file read -> endpoint handlers (serve_api)
- status -> read index file -> print summary
- hook_remove -> unlink hook scripts -> clean config

## Structure
| Wiki Page | Covers | Entry Points |
|-----------|--------|--------------|
| wiki/root.md | indexer/cli.py | main, init, status, hook, hook_install, hook_remove, serve, serve_api |
## Last Indexed
Commit: 50ff6f37c75bb4f71422cc106db3856a86ed44c3 — 2026-04-28