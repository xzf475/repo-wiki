# ./

## Overview

This module is the CLI entry point for the codebase indexing system, implemented as a Click command group. It exposes subcommands (init, run, status, hook install/remove, serve, serve_api) that orchestrate configuration setup, file indexing with enrichment, wiki page generation, pre-commit hook management, and serving via MCP or REST API. The functions `_ensure_cache_gitignore` and `_is_indexable` provide internal guards against cache tracking and non-indexable files. This layer abstracts the underlying indexing, enrichment, and serving components (like `deep_enrich_index`, `write_wiki_pages`, `create_api_server`) into a unified CLI. It solves the problem of providing a single user-facing interface for all indexing lifecycle operations across repositories.

## Modules
| File | Purpose |
|------|---------|
| indexer/cli.py | CLI for indexing codebase, managing hooks, and serving MCP/REST APIs |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `indexer/cli.py::main` | function | Entry point CLI group using click, dispatches subcommands |
| `indexer/cli.py::init` | function | Creates config, installs pre-commit hook, appends to CLAUDE.md |
| `indexer/cli.py::run` | function | Indexes codebase, generates wiki pages using enrichment and vector upsert |
| `indexer/cli.py::status` | function | Shows last commit, stale files, and manifest stats |
| `indexer/cli.py::hook` | function | CLI group for managing pre-commit hooks |
| `indexer/cli.py::hook_install` | function | Installs pre-commit hook in current repo |
| `indexer/cli.py::hook_remove` | function | Removes pre-commit hook from current repo |
| `indexer/cli.py::serve` | function | Starts MCP server for semantic code search |
| `indexer/cli.py::serve_api` | function | Starts REST API server for remote semantic code search across repos |
| `indexer/cli.py::_ensure_cache_gitignore` | function | Ensures cache directory includes .gitignore to prevent tracking |
| `indexer/cli.py::_is_indexable` | function | Checks if file path matches indexable patterns using fnmatch |
## Data Flows
- User runs `indexer init` → checks git repo, creates config file, installs pre-commit hook via `install_hook`, appends to CLAUDE.md, ensures cache .gitignore via `_ensure_cache_gitignore`
- User runs `indexer run` → loads manifest via `load_manifest`, filters files via `_is_indexable`, calls `deep_enrich_index`, then calls `write_wiki_pages` to persist indexed wiki pages
- User runs `indexer status` → loads config and manifest, gets all tracked files via `all_tracked_files`, computes stale files via `stale_files`, displays last commit and stats
- User runs `indexer serve` or `serve_api` → resolves cwd, starts MCP server via `create_server` (with transport option) or REST API via `create_app`, blocking on `run`
## Design Constraints
- Cache directory is explicitly protected from git tracking by writing a .gitignore file (contents: ``) inside it; missing or partial .gitignore is appended without duplication
- The `_is_indexable` helper uses `fnmatch` with predefined patterns (not configurable via CLI) and operates on `Path` objects, not strings
- Both `serve` and `serve_api` block indefinitely via `run`; the MCP server transport is restricted to a `Choice` of 'stdio' or 'sse'
- The `run` command calls `setdefault` on the config dictionary before enrichment (to ensure a default key exists), indicating a mutable config passed through
- `init` only proceeds if the current directory is a git repository (`is_git_repo` must return truthy); no fallback for non-git directories
- Pre-commit hook install/remove (`hook_install`, `hook_remove`) use `install_hook`/`remove_hook` from an external module and echo success/failure messages, but do not validate hook state before removal
## Relationships
- **Calls:** Choice, Path, _ensure_cache_gitignore, _is_indexable, all_tracked_files, any, append, build_batches, changed_files_since, command, compute_hash_short, create_api_server, create_app, create_server, cross_reference, current_branch, cwd, deep_enrich_index, deep_enrich_pages, density_group, describe_files, describe_nodes, echo, exists, extend, fnmatch, get, group, install_hook, is_dir, is_git_repo, items, iterdir, join, len, list, load_cached_nodes, load_config, load_existing_nodes, load_manifest, lstrip, option, parse_file, read_text, remove_hook, removed_files, replace, resolve, rstrip, run, save_cached_nodes, save_config, set, setdefault, split, staged_files, stale_files, str, sum, synthesize_commit_message, update_manifest, upsert_vectors, values, warn, write_index_and_skill, write_text, write_wiki_pages
- **Called by:** indexer/cli.py::init, indexer/cli.py::run, indexer/cli.py::serve, indexer/cli.py::serve_api, indexer/cli.py::status, indexer/git.py::_run, indexer/git.py::is_git_repo, indexer/rest_api.py::_detect_default_branch, indexer/rest_api.py::_run_rebuild_task, indexer/rest_api.py::_run_register_task_inner, indexer/rest_api.py::_run_sync_task, indexer/rest_api.py::_store_credentials, indexer/rest_api.py::list_repos, indexer/rest_api.py::validate_repo
- **Imports from:** __future__.annotations, click, datetime.datetime, datetime.timezone, fnmatch.fnmatch, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.load_config, indexer.config.save_config, indexer.git.all_tracked_files, indexer.git.changed_files_since, indexer.git.current_branch, indexer.git.current_commit, indexer.git.is_git_repo, indexer.git.staged_files, indexer.grouper.density_group, indexer.hooks.install_hook, indexer.hooks.remove_hook, indexer.indexing.build_batches, indexer.indexing.cross_reference, indexer.indexing.load_existing_nodes, indexer.indexing.parse_candidates, indexer.indexing.update_manifest, indexer.indexing.upsert_vectors, indexer.indexing.write_index_and_skill, indexer.indexing.write_wiki_pages, indexer.llm.deep_enrich_index, indexer.llm.deep_enrich_page, indexer.llm.deep_enrich_pages, indexer.llm.describe_files, indexer.llm.describe_nodes, indexer.llm.synthesize_commit_message, indexer.manifest.FileEntry, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.mcp_server.create_api_server, indexer.mcp_server.create_server, indexer.rest_api.create_app, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.TEMPLATES_DIR, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_index, indexer.wiki.write_page, os, pathlib.Path, subprocess, uvicorn, warnings
## Entry Points
- `main`
- `init`
- `status`
- `hook`
- `hook_install`
- `hook_remove`
- `serve`
- `serve_api`
