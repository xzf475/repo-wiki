# Agent Integration Guide

All adapters read one published `RepositoryIndex` generation. Agents should carry repository, branch, generation, and tree ID through a task so later reads can detect drift.

## Recommended flow

1. Read status with `repo-wiki status`, `get_index_status_tool`, or `POST /index-status`.
2. If stale, run `repo-wiki run`, `POST /sync`, or `POST /sync-all`.
3. Search with an explicit repository and branch.
4. Treat `matches` as query answers and `related` as graph context.
5. Resolve the exact component ID before editing.
6. Fetch bounded source/edit context.
7. Re-check generation before applying a long-running change.
8. Run post-edit verification against the actual diff.

## Retrieval policy

Choose the weakest mode that satisfies the task:

| Mode | Use when | Failure behavior |
|---|---|---|
| `local` | Deterministic navigation, CI, hooks | Exact + FTS5 + Graph only |
| `preferred` | General coding-agent search | Uses dense when ready; reports degradation otherwise |
| `required` | The task explicitly requires semantic recall | Fails instead of silently degrading |

Do not infer dense readiness from the presence of files. Read `dense_state`, `retrieval`, and `degradations`.

## Local CLI

```bash
repo-wiki status
repo-wiki run
repo-wiki agent context --symbol-id src/auth.py::validate_token
repo-wiki agent plan --goal "fix token validation" --symbol-id src/auth.py::validate_token
repo-wiki agent verify
```

The pre-commit hook publishes the staged tree with `repo-wiki run --staged`. This structural generation is complete and searchable without an embedding provider.

## MCP

Start a local server from the repository root:

```bash
repo-wiki serve
```

Or route MCP through a multi-repository REST deployment:

```bash
repo-wiki serve --api http://localhost:7654
```

Primary tools:

- `get_index_status_tool`: establish generation and freshness.
- `search_symbols_tool`: retrieve ranked matches and related graph context.
- `resolve_symbol_tool`: choose an exact component ID.
- `get_source_context_tool` / `get_edit_context_tool`: fetch bounded source.
- `trace_call_tool` / `impact_analysis_tool`: inspect dependencies.
- `find_tests_for_symbol_tool` / `post_edit_verify_tool`: plan validation.

Multi-repository MCP search must pass `branch` for any repository with more than one indexed branch.

## REST example

```bash
curl -sS -X POST http://localhost:7654/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query":"payment callback signature verification",
    "repo":"backend",
    "branch":"main",
    "top_k":8,
    "expand_depth":1,
    "retrieval":"preferred"
  }'
```

Record these response fields in the agent trace:

- `search_metrics[].repo` and `branch`
- `search_metrics[].generation` and `tree_id`
- `search_metrics[].retrieval` and `degradations`
- result `id`, file, line range, and score breakdown

## Health semantics

`GET /api/validate/{name}` checks:

- `.indexer.toml`
- `.indexer/state/repository-index.sqlite3`
- SQLite page integrity and foreign keys
- one published generation per registered branch
- source-tree freshness
- `wiki/INDEX.md`
- `.indexer/skills/codebase.md`

Dense enrichment is optional and therefore informational rather than a structural health requirement.

## Drift handling

Before editing, compare the search generation/tree with current status. If they differ, discard previously fetched locations and search again. A component ID can remain textually identical while its implementation or call edges have changed.

## Security

- Keep Git and embedding credentials in environment variables or request-secret fields; never place them in generated Wiki pages.
- Use `REPO_WIKI_API_KEY` for REST Bearer authentication.
- Use `WEBHOOK_SECRET` to validate webhook signatures.
- Source endpoints reject paths that escape the registered repository root.
