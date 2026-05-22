# Agent Integration Guide

repo-wiki is designed to be used by local and remote coding Agents before and after edits.

## Local CLI Flow

Use this when the Agent runs in the same checkout as the code.

```bash
repo-wiki agent capabilities
repo-wiki agent context --symbol-id src/auth.py::validate_token
repo-wiki agent plan --goal "fix token validation" --symbol-id src/auth.py::validate_token
repo-wiki agent verify
repo-wiki agent diagnose
```

`repo-wiki agent verify` reads the local `git diff` when no diff file is supplied, so it can be used before commit.

## Remote REST Flow

Use this when the Agent calls a repo-wiki server that cannot see the Agent's uncommitted workspace.

```bash
curl http://localhost:8765/agent-schema

curl -X POST http://localhost:8765/resolve-symbol \
  -H 'Content-Type: application/json' \
  -d '{"repo":"backend","query":"login endpoint"}'

curl -X POST http://localhost:8765/change-plan \
  -H 'Content-Type: application/json' \
  -d '{"repo":"backend","goal":"fix token validation","symbol_id":"src/auth.py::validate_token"}'

git diff > /tmp/agent.diff
curl -X POST http://localhost:8765/post-edit-verify \
  -H 'Content-Type: application/json' \
  --data-binary @<(jq -n --rawfile diff /tmp/agent.diff '{repo:"backend", diff:$diff}')
```

Remote callers should pass either `diff` or `changed_files` for pre-commit validation. Without that payload, the server can only analyze committed/indexed repository state.

## MCP Flow

For Codex, Claude, Cursor, or other MCP clients:

1. Call `agent_capabilities_manifest_tool` to discover available tools.
2. Locate code with `locate_from_error_tool`, `search_symbols_tool`, or `resolve_symbol_tool`.
3. Read context with `get_edit_context_tool`.
4. Plan with `impact_analysis_tool` and `change_plan_tool`.
5. After editing, call `post_edit_verify_tool`.
6. If the index looks stale or incomplete, call `diagnose_index_tool`.

## Machine-Readable Contracts

Two contracts are available:

- `GET /agent-capabilities`: compact tool manifest with examples and next-tool hints.
- `GET /agent-schema`: OpenAPI 3.1 document with request and response schemas.

These endpoints let remote Agents discover how to call repo-wiki without scraping prose docs.

## Index Health

`diagnose_index` returns:

- `summary`: manifest file count, missing source/wiki counts, stale/removed counts, artifact presence.
- `checks.manifest`, `checks.wiki_index`, `checks.skill_file`, `checks.vector_db`.
- `checks.source_files` and `checks.wiki_pages` with sampled missing paths.
- `checks.consistency` with manifest-to-source/wiki ratios.
- `checks.freshness` with commit and file freshness status.
