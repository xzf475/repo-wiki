# Agent Tool Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the Agent-facing code-location toolchain so every capability works reliably in both local MCP mode and remote REST/MCP proxy mode.

**Architecture:** Keep the existing shape: core logic in `indexer/retrieval.py`, thin REST wrappers in `indexer/rest_api.py`, local and remote MCP wrappers in `indexer/mcp_server.py`, metadata enrichment in parsers/vector metadata, and regression coverage in `tests/test_agent_context.py` plus focused endpoint/E2E tests. All remote tools that need local-only state must accept explicit payloads such as `diff`, `changed_files`, or snapshot nodes.

**Tech Stack:** Python 3.12, Starlette REST API, MCP FastMCP, pytest, git CLI, existing repo-wiki manifest/vector store abstractions.

---

## File Structure

- Modify `indexer/retrieval.py`: shared pagination/detail shaping, diff validation, schema helpers, enhanced entry point detection, cross-repo graph parsing, stable ID migration report.
- Modify `indexer/rest_api.py`: request validation, payload limits, new/updated endpoint contracts, schema endpoint output.
- Modify `indexer/mcp_server.py`: mirror all REST functionality in local MCP and remote MCP proxy tools.
- Modify `indexer/vector_store.py`: store stable IDs and richer entry point metadata in vector metadata.
- Modify parser files as needed: `indexer/ast_parser.py`, `indexer/js_parser.py`, `indexer/go_parser.py`, `indexer/java_parser.py`, `indexer/ruby_parser.py`, `indexer/rust_parser.py` for AST-level entry points.
- Add or modify tests in `tests/test_agent_context.py`, `tests/test_api_contracts.py`, and `tests/test_agent_e2e.py`.
- Update docs: `README.md`, `docs/api-reference.md`, `skills/SKILL.md`, `.indexer/skills/codebase.md`.

---

### Task 1: Response Slimming and Pagination

**Files:**
- Modify: `indexer/retrieval.py`
- Modify: `indexer/rest_api.py`
- Modify: `indexer/mcp_server.py`
- Test: `tests/test_agent_context.py`

- [ ] **Step 1: Write failing tests**

Add tests that assert large tools support `max_results` and `include_details`:

```python
def test_change_set_respects_max_results_and_summary(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import change_set

    monkeypatch.setattr("indexer.retrieval.post_edit_verify", lambda *a, **k: {
        "changed_files": [f"src/f{i}.py" for i in range(20)],
        "changed_symbols": [{"id": f"src/f{i}.py::fn", "file": f"src/f{i}.py"} for i in range(20)],
        "verify_commands": ["python3 -m pytest"],
    })
    monkeypatch.setattr("indexer.retrieval.impact_analysis", lambda *a, **k: {
        "symbol": None, "direct_callers": [], "direct_callees": [],
        "candidate_tests": [], "affected_files": [], "risk_points": [],
    })

    result = change_set("goal", Config(), tmp_path, diff="diff", max_results=5, include_details=False)

    assert result["summary"]["changed_file_count"] == 20
    assert len(result["must_change_files"]) == 5
    assert "details_omitted" in result
```

- [ ] **Step 2: Verify red**

Run: `python3.12 -m pytest tests/test_agent_context.py::test_change_set_respects_max_results_and_summary -q`

Expected: FAIL because `change_set` does not accept `max_results` or `include_details`.

- [ ] **Step 3: Implement shared shaping**

Add helpers:

```python
def _limit_list(items: list, max_results: int) -> list:
    return items[:max(1, min(max_results, 500))]

def _result_summary(items: list, label: str) -> dict:
    return {f"{label}_count": len(items)}
```

Update heavy retrieval functions: `change_set`, `coverage_map`, `index_diff_report`, `cross_repo_graph`, `post_edit_verify`, `locate_from_error`, `list_entry_points`.

- [ ] **Step 4: Thread params through REST and MCP**

REST request fields:
- `max_results`: default per tool, hard cap 500
- `include_details`: default `true`

MCP local/proxy wrappers pass both fields.

- [ ] **Step 5: Verify green**

Run:
- `python3.12 -m pytest tests/test_agent_context.py -q`
- `python3.12 -m pytest -q`

Expected: all pass.

---

### Task 2: Remote Diff Size Protection

**Files:**
- Modify: `indexer/rest_api.py`
- Modify: `indexer/retrieval.py`
- Modify: `indexer/mcp_server.py`
- Test: `tests/test_agent_context.py`

- [ ] **Step 1: Write failing tests**

```python
def test_post_edit_verify_rejects_oversized_diff(monkeypatch):
    import asyncio
    from starlette.requests import Request
    from indexer.rest_api import post_edit_verify

    body = {"repo": "demo", "diff": "x" * (2 * 1024 * 1024 + 1)}
    request = make_json_request(body)
    response = asyncio.run(post_edit_verify(request))

    assert response.status_code == 413
```

Use existing request-test helpers if present; otherwise add a small local helper in the test file.

- [ ] **Step 2: Verify red**

Run: `python3.12 -m pytest tests/test_agent_context.py::test_post_edit_verify_rejects_oversized_diff -q`

Expected: FAIL because no 413 limit exists.

- [ ] **Step 3: Add size policy**

In `rest_api.py`:

```python
MAX_DIFF_BYTES = int(os.environ.get("REPO_WIKI_MAX_DIFF_BYTES", str(2 * 1024 * 1024)))

def _validate_diff_payload(diff: str) -> JSONResponse | None:
    if len(diff.encode("utf-8", errors="replace")) > MAX_DIFF_BYTES:
        return JSONResponse(
            {"error": f"diff payload too large; max {MAX_DIFF_BYTES} bytes"},
            status_code=413,
        )
    return None
```

Apply to `/post-edit-verify`, `/change-set`, and any future diff-consuming endpoint.

- [ ] **Step 4: Add MCP docstrings**

Local MCP can omit `diff`. Remote MCP docstrings must say: pass diff, size limit applies.

- [ ] **Step 5: Verify**

Run:
- `python3.12 -m pytest tests/test_agent_context.py -q`
- `python3.12 -m pytest -q`

---

### Task 3: Tool Contract Tests

**Files:**
- Create: `tests/test_api_contracts.py`
- Modify: `indexer/rest_api.py`
- Modify: `indexer/mcp_server.py`

- [ ] **Step 1: Write contract tests for response fields**

Add tests for:
- `/resolve-symbol`
- `/impact-analysis`
- `/change-plan`
- `/change-set`
- `/post-edit-verify`
- `/coverage-map`
- `/index-diff-report`
- `/agent-capabilities`

Each test asserts stable top-level keys, not exact full payload.

```python
def assert_keys(payload, keys):
    for key in keys:
        assert key in payload

def test_agent_capabilities_contract():
    from indexer.retrieval import agent_capabilities_manifest
    payload = agent_capabilities_manifest()
    assert_keys(payload, ["local_and_remote", "tools", "recommended_flow"])
```

- [ ] **Step 2: Verify red for missing schema details**

Add a test requiring every tool in `agent_capabilities_manifest()["tools"]` to have `input_schema`, `output_schema`, and `example`.

Expected: FAIL because current manifest is only a list.

- [ ] **Step 3: Implement schema-rich capabilities**

Return:

```python
{
  "local_and_remote": True,
  "tools": {
    "post_edit_verify_tool": {
      "modes": ["local", "remote"],
      "input_schema": {...},
      "output_schema": {...},
      "example": {...},
      "next_tools": [...]
    }
  },
  "recommended_flow": [...]
}
```

- [ ] **Step 4: Verify**

Run:
- `python3.12 -m pytest tests/test_api_contracts.py -q`
- `python3.12 -m pytest -q`

---

### Task 4: Real Small-Repo E2E

**Files:**
- Create: `tests/test_agent_e2e.py`
- Modify only production code if the E2E exposes a defect.

- [ ] **Step 1: Write E2E test**

Create temp git repo:
- `src/auth.py` with `validate_token`
- `src/api.py` with login handler docstring `POST /login endpoint`
- `tests/test_auth.py`
- initialize git
- run index pipeline through existing CLI or direct indexing functions
- call:
  - `locate_from_error`
  - `change_set`
  - `post_edit_verify`

Expected:
- error maps to `src/auth.py::validate_token`
- change set includes `src/api.py` and `tests/test_auth.py`
- post-edit verify recommends pytest command

- [ ] **Step 2: Verify red**

Run: `python3.12 -m pytest tests/test_agent_e2e.py -q`

Expected: FAIL until setup wiring is complete.

- [ ] **Step 3: Implement minimal E2E support**

If direct vector indexing is too heavy, use the existing vector store monkeypatch pattern only for unit tests, but the E2E should exercise real manifest + parser + retrieval helpers where possible.

- [ ] **Step 4: Verify**

Run:
- `python3.12 -m pytest tests/test_agent_e2e.py -q`
- `python3.12 -m pytest -q`

---

### Task 5: AST-Level Entry Point Detection

**Files:**
- Modify: `indexer/ast_parser.py`
- Modify: `indexer/js_parser.py`
- Modify: `indexer/vector_store.py`
- Test: `tests/test_ast_parser.py`
- Test: `tests/test_agent_context.py`

- [ ] **Step 1: Write parser tests**

Python cases:
- FastAPI decorator: `@app.post("/login")`
- Flask decorator: `@bp.route("/login", methods=["POST"])`
- Click command: `@click.command()`
- Typer app command: `@app.command()`

JS cases:
- Express route: `app.post("/login", handler)`
- React event prop/function names: `onClick`, `handleSubmit`

Assert parsed nodes carry entry metadata if ASTNode is extended, or vector metadata marks these nodes as entry points.

- [ ] **Step 2: Verify red**

Run selected parser tests. Expected: FAIL.

- [ ] **Step 3: Extend metadata without breaking cache**

Preferred low-risk path:
- Do not require changing `ASTNode` constructor for every parser unless needed.
- Add optional `entry_point_kind: str = ""` and `entry_point_path: str = ""` to `ASTNode`.
- Update cache load to tolerate missing fields.
- Update `_build_meta` to use explicit entry metadata before heuristics.

- [ ] **Step 4: Implement Python and JS detection**

Python:
- inspect decorators in `ast.FunctionDef.decorator_list`
- detect `.get`, `.post`, `.put`, `.patch`, `.delete`, `.route`, `.command`

JS:
- detect route calls and handler function names where existing parser exposes enough structure.

- [ ] **Step 5: Verify**

Run:
- `python3.12 -m pytest tests/test_ast_parser.py -q`
- `python3.12 -m pytest tests/test_agent_context.py -q`
- `python3.12 -m pytest -q`

---

### Task 6: Cross-Repo Graph Enhancement

**Files:**
- Modify: `indexer/retrieval.py`
- Test: `tests/test_agent_context.py`

- [ ] **Step 1: Write failing tests**

Add cases for:
- `fetch("/api/users")`
- `axios.post("/login")`
- OpenAPI path strings
- GraphQL operation name shared by client/server text

- [ ] **Step 2: Verify red**

Run cross-repo graph tests. Expected: FAIL for axios/OpenAPI/GraphQL cases.

- [ ] **Step 3: Implement extractors**

Add helpers:

```python
def _extract_client_paths(text: str) -> list[str]:
    # fetch, axios, raw HTTP method/path

def _extract_graphql_operations(text: str) -> list[str]:
    # query/mutation OperationName
```

Edges:
- `kind="http_path"`
- `kind="graphql_operation"`
- `kind="openapi_path"`

- [ ] **Step 4: Verify**

Run:
- `python3.12 -m pytest tests/test_agent_context.py -q`
- `python3.12 -m pytest -q`

---

### Task 7: Stable ID Migration Report

**Files:**
- Modify: `indexer/retrieval.py`
- Modify: `indexer/vector_store.py`
- Test: `tests/test_agent_context.py`

- [ ] **Step 1: Write failing test**

```python
def test_index_diff_report_detects_rename_by_stable_id(tmp_path):
    before = [{"id": "src/a.py::old_name", "metadata": {"stable_symbol_id": "sym:abc"}}]
    after = [{"id": "src/b.py::new_name", "metadata": {"stable_symbol_id": "sym:abc"}}]

    result = index_diff_report(Config(), tmp_path, before_nodes=before, after_nodes=after)

    assert result["renamed_or_moved_symbols"] == [{
        "stable_symbol_id": "sym:abc",
        "before": "src/a.py::old_name",
        "after": "src/b.py::new_name",
    }]
```

- [ ] **Step 2: Verify red**

Run selected test. Expected: FAIL because current report emits delete+add.

- [ ] **Step 3: Implement stable matching**

In `index_diff_report`, build maps by `metadata.stable_symbol_id`. Remove matched pairs from added/removed lists and emit `renamed_or_moved_symbols`.

- [ ] **Step 4: Verify**

Run:
- `python3.12 -m pytest tests/test_agent_context.py -q`
- `python3.12 -m pytest -q`

---

### Task 8: Tool Capability Self-Description Schema

**Files:**
- Modify: `indexer/retrieval.py`
- Modify: `docs/api-reference.md`
- Test: `tests/test_api_contracts.py`

- [ ] **Step 1: Write failing schema completeness test**

```python
def test_agent_capabilities_all_tools_have_schemas():
    from indexer.retrieval import agent_capabilities_manifest
    manifest = agent_capabilities_manifest()
    for name, spec in manifest["tools"].items():
        assert spec["input_schema"]
        assert spec["output_schema"]
        assert spec["example"]
        assert "local" in spec["modes"] or "remote" in spec["modes"]
```

- [ ] **Step 2: Verify red**

Expected: FAIL until manifest is schema-rich.

- [ ] **Step 3: Implement complete manifest**

Cover all Agent-facing tools:
- `search_symbols_tool`
- `resolve_symbol_tool`
- `locate_from_error_tool`
- `impact_analysis_tool`
- `change_plan_tool`
- `change_set_tool`
- `post_edit_verify_tool`
- `coverage_map_tool`
- `index_diff_report_tool`
- `cross_repo_graph_tool`
- `diagnose_index_tool`
- `agent_protocol_tool`
- `agent_capabilities_manifest_tool`

- [ ] **Step 4: Verify**

Run:
- `python3.12 -m pytest tests/test_api_contracts.py -q`
- `python3.12 -m pytest -q`

---

## Final Verification

- [ ] Run `python3.12 -m pytest -q`
- [ ] Run `git status --short`
- [ ] Inspect `git diff --stat`
- [ ] Confirm docs mention local and remote behavior for every new/changed tool.
- [ ] Confirm remote tools that need local state accept explicit payloads.

## Execution Order

1. Response slimming and pagination
2. Remote diff size protection
3. Tool contract tests
4. Real small-repo E2E
5. AST-level entry point detection
6. Cross-repo graph enhancement
7. Stable ID migration report
8. Tool capability self-description schema

This order reduces risk: first prevent oversized outputs/inputs, then lock contracts, then expand parsing and graph intelligence.
