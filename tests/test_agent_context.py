from pathlib import Path


def test_index_status_reports_stale_manifest_entry(tmp_path):
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import get_index_status

    src = tmp_path / "app.py"
    src.write_text("def old():\n    return 1\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit="abc123",
            indexed_at="2026-01-01T00:00:00Z",
            files={
                "app.py": FileEntry(
                    hash="sha256:not-current",
                    wiki_page="wiki/app.md",
                    component_ids=["app.py::old"],
                )
            },
        ),
    )

    status = get_index_status(tmp_path)

    assert status["is_stale"] is True
    assert status["stale_files"] == ["app.py"]
    assert status["indexed_commit"] == "abc123"


def test_find_tests_for_symbol_matches_file_and_symbol(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import find_tests_for_symbol

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "auth.py").write_text("def validate_token():\n    return True\n")
    (tmp_path / "tests" / "test_auth.py").write_text(
        "from src.auth import validate_token\n\n"
        "def test_validate_token():\n"
        "    assert validate_token()\n"
    )
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry("sha256:x", "wiki/src.md", ["src/auth.py::validate_token"]),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )

    monkeypatch.setattr(
        "indexer.retrieval.get_by_ids",
        lambda ids, vector_store, repo_root: [
            {
                "id": "src/auth.py::validate_token",
                "metadata": {"file": "src/auth.py", "line_start": 1, "line_end": 2},
                "document": "validate token",
            }
        ],
    )

    matches = find_tests_for_symbol("src/auth.py::validate_token", Config(), tmp_path)

    assert matches[0]["file"] == "tests/test_auth.py"
    assert "symbol name match" in matches[0]["reasons"]


def test_get_edit_context_includes_source_relations_tests_and_status(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import get_edit_context

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "auth.py").write_text(
        "def caller():\n"
        "    return validate_token()\n\n"
        "def validate_token():\n"
        "    return True\n"
    )
    (tmp_path / "tests" / "test_auth.py").write_text("def test_validate_token():\n    pass\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry(
                    "sha256:x",
                    "wiki/src.md",
                    ["src/auth.py::caller", "src/auth.py::validate_token"],
                ),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )

    nodes = {
        "src/auth.py::validate_token": {
            "id": "src/auth.py::validate_token",
            "metadata": {
                "file": "src/auth.py",
                "line_start": 4,
                "line_end": 5,
                "type": "function",
                "calls": "[]",
                "called_by": "[\"src/auth.py::caller\"]",
                "imports": "[]",
            },
            "document": "validate token",
        },
        "src/auth.py::caller": {
            "id": "src/auth.py::caller",
            "metadata": {"file": "src/auth.py", "line_start": 1, "line_end": 2, "type": "function"},
            "document": "caller",
        },
    }
    monkeypatch.setattr(
        "indexer.retrieval.get_by_ids",
        lambda ids, vector_store, repo_root: [nodes[i] for i in ids if i in nodes],
    )

    context = get_edit_context("src/auth.py::validate_token", Config(), tmp_path)

    assert context["symbol"]["id"] == "src/auth.py::validate_token"
    assert "def validate_token" in context["source"]
    assert context["callers"][0]["id"] == "src/auth.py::caller"
    assert context["candidate_tests"][0]["file"] == "tests/test_auth.py"
    assert "index_status" in context


def test_rest_routes_expose_agent_context_tools():
    import inspect

    import indexer.rest_api as api

    src = inspect.getsource(api.create_app)
    assert 'Route("/edit-context"' in src
    assert 'Route("/tests-for-symbol"' in src
    assert 'Route("/index-status"' in src
    assert 'Route("/resolve-symbol"' in src
    assert 'Route("/pre-edit-check"' in src
    assert 'Route("/impact-analysis"' in src
    assert 'Route("/change-plan"' in src
    assert 'Route("/diagnose-index"' in src
    assert 'Route("/agent-protocol"' in src
    assert 'Route("/locate-from-error"' in src
    assert 'Route("/entry-points"' in src
    assert 'Route("/post-edit-verify"' in src
    assert 'Route("/change-set"' in src
    assert 'Route("/coverage-map"' in src
    assert 'Route("/index-diff-report"' in src
    assert 'Route("/cross-repo-graph"' in src
    assert 'Route("/agent-capabilities"' in src
    assert 'Route("/stable-symbol-id"' in src


def test_mcp_servers_expose_agent_context_tools():
    import inspect

    import indexer.mcp_server as mcp_server

    single = inspect.getsource(mcp_server.create_server)
    proxy = inspect.getsource(mcp_server.create_api_server)
    for src in (single, proxy):
        assert "get_edit_context_tool" in src
        assert "find_tests_for_symbol_tool" in src
        assert "get_index_status_tool" in src
        assert "resolve_symbol_tool" in src
        assert "pre_edit_check_tool" in src
        assert "impact_analysis_tool" in src
        assert "change_plan_tool" in src
        assert "diagnose_index_tool" in src
        assert "agent_protocol_tool" in src
        assert "locate_from_error_tool" in src
        assert "list_entry_points_tool" in src
        assert "post_edit_verify_tool" in src
        assert "change_set_tool" in src
        assert "coverage_map_tool" in src
        assert "index_diff_report_tool" in src
        assert "cross_repo_graph_tool" in src
        assert "agent_capabilities_manifest_tool" in src
        assert "stable_symbol_id_tool" in src


def test_resolve_symbol_ranks_exact_name_and_path(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import resolve_symbol

    hits = [
        {
            "id": "src/payments.py::charge_user",
            "metadata": {"file": "src/payments.py", "type": "function", "line_start": 10, "line_end": 20},
            "document": "charge user",
        },
        {
            "id": "src/auth.py::charge_user",
            "metadata": {"file": "src/auth.py", "type": "function", "line_start": 1, "line_end": 5},
            "document": "charge auth",
        },
    ]
    monkeypatch.setattr("indexer.retrieval.search_symbols", lambda *args, **kwargs: hits)

    result = resolve_symbol("charge_user", Config(), tmp_path, file_hint="payments.py")

    assert result["status"] == "resolved"
    assert result["symbol"]["id"] == "src/payments.py::charge_user"
    assert "file hint match" in result["symbol"]["match_reasons"]


def test_search_symbols_can_explain_hits(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import search_symbols

    monkeypatch.setattr("indexer.retrieval.embed_query", lambda query, cfg: [0.1])
    monkeypatch.setattr(
        "indexer.retrieval.search",
        lambda *args, **kwargs: [
            {
                "id": "src/auth.py::validate_token",
                "metadata": {"file": "src/auth.py", "type": "function"},
                "document": "Validate JWT token",
                "distance": 0.2,
            }
        ],
    )

    hits = search_symbols("validate token", Config(), tmp_path, expand_depth=0, explain=True)

    assert hits[0]["match_reasons"]
    assert "distance=0.2" in hits[0]["match_reasons"]
    assert "query token match" in hits[0]["match_reasons"]


def test_pre_edit_check_reports_dirty_files_and_test_commands(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import pre_edit_check

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "src" / "auth.py").write_text("def validate_token():\n    return True\n")
    (tmp_path / "tests" / "test_auth.py").write_text("def test_validate_token():\n    pass\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry("sha256:x", "wiki/src.md", ["src/auth.py::validate_token"]),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )
    monkeypatch.setattr("indexer.retrieval._git_dirty_files", lambda repo_root: ["src/auth.py"])
    monkeypatch.setattr(
        "indexer.retrieval.get_by_ids",
        lambda ids, vector_store, repo_root: [
            {
                "id": "src/auth.py::validate_token",
                "metadata": {"file": "src/auth.py", "line_start": 1, "line_end": 2},
                "document": "validate token",
            }
        ],
    )

    check = pre_edit_check("src/auth.py::validate_token", Config(), tmp_path)

    assert check["dirty_files"] == ["src/auth.py"]
    assert check["candidate_tests"][0]["file"] == "tests/test_auth.py"
    assert "python3 -m pytest tests/test_auth.py" in check["recommended_commands"]


def test_impact_analysis_collects_transitive_relations_tests_and_files(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import impact_analysis

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "auth.py").write_text("def login():\n    return validate_token()\n")
    (tmp_path / "tests" / "test_auth.py").write_text("def test_validate_token():\n    pass\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry(
                    "sha256:x",
                    "wiki/src.md",
                    ["src/auth.py::login", "src/auth.py::validate_token", "src/auth.py::decode_token"],
                ),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )
    nodes = {
        "src/auth.py::validate_token": {
            "id": "src/auth.py::validate_token",
            "metadata": {
                "file": "src/auth.py",
                "type": "function",
                "calls": "[\"src/auth.py::decode_token\"]",
                "called_by": "[\"src/auth.py::login\"]",
            },
            "document": "validate token",
        },
        "src/auth.py::login": {
            "id": "src/auth.py::login",
            "metadata": {"file": "src/auth.py", "type": "function", "calls": "[\"src/auth.py::validate_token\"]"},
            "document": "POST /login handler",
        },
        "src/auth.py::decode_token": {
            "id": "src/auth.py::decode_token",
            "metadata": {"file": "src/auth.py", "type": "function", "called_by": "[\"src/auth.py::validate_token\"]"},
            "document": "decode token",
        },
    }
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [nodes[i] for i in ids if i in nodes])

    impact = impact_analysis("src/auth.py::validate_token", Config(), tmp_path, max_depth=2)

    assert impact["symbol"]["id"] == "src/auth.py::validate_token"
    assert impact["direct_callers"][0]["id"] == "src/auth.py::login"
    assert impact["direct_callees"][0]["id"] == "src/auth.py::decode_token"
    assert impact["candidate_tests"][0]["file"] == "tests/test_auth.py"
    assert "src/auth.py" in impact["affected_files"]
    assert impact["entry_points"][0]["id"] == "src/auth.py::login"


def test_change_plan_returns_agent_edit_steps_and_commands(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import change_plan

    monkeypatch.setattr(
        "indexer.retrieval.pre_edit_check",
        lambda symbol_id, cfg, repo_root: {
            "index_status": {"is_stale": False, "reasons": []},
            "dirty_files": [],
            "candidate_tests": [{"file": "tests/test_auth.py"}],
            "recommended_commands": ["python3 -m pytest tests/test_auth.py"],
            "callers": [],
            "callees": [],
        },
    )
    monkeypatch.setattr(
        "indexer.retrieval.impact_analysis",
        lambda symbol_id, cfg, repo_root, max_depth=2: {
            "symbol": {"id": symbol_id, "metadata": {"file": "src/auth.py", "line_start": 10, "line_end": 20}},
            "affected_files": ["src/auth.py", "tests/test_auth.py"],
            "risk_points": ["No direct callers found"],
        },
    )

    plan = change_plan("change login validation", "src/auth.py::validate_token", Config(), tmp_path)

    assert plan["target_symbol_id"] == "src/auth.py::validate_token"
    assert plan["read_these_files"][0]["file"] == "src/auth.py"
    assert plan["edit_targets"][0]["symbol_id"] == "src/auth.py::validate_token"
    assert "python3 -m pytest tests/test_auth.py" in plan["verify_commands"]
    assert plan["steps"][0].startswith("Confirm index freshness")


def test_diagnose_index_reports_missing_wiki_vector_and_missing_sources(tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import diagnose_index

    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit="abc123",
            indexed_at="",
            files={"src/missing.py": FileEntry("sha256:x", "wiki/missing.md", ["src/missing.py::gone"])},
        ),
    )

    report = diagnose_index(tmp_path, Config())

    assert report["healthy"] is False
    assert report["checks"]["wiki_index"]["ok"] is False
    assert report["checks"]["vector_db"]["ok"] is False
    assert report["checks"]["source_files"]["missing"] == ["src/missing.py"]
    assert "summary" in report
    assert report["summary"]["manifest_file_count"] == 1
    assert report["summary"]["missing_source_count"] == 1
    assert report["checks"]["consistency"]["manifest_to_source_ratio"] == 0.0


def test_agent_protocol_bundle_is_compact_and_includes_freshness(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import agent_protocol_bundle

    monkeypatch.setattr(
        "indexer.retrieval.change_plan",
        lambda goal, symbol_id, cfg, repo_root: {
            "goal": goal,
            "target_symbol_id": symbol_id,
            "index_status": {"is_stale": True, "reasons": ["HEAD differs from indexed commit"]},
            "read_these_files": [{"file": "src/auth.py", "line_start": 1, "line_end": 20}],
            "edit_targets": [{"file": "src/auth.py", "symbol_id": symbol_id}],
            "verify_commands": ["python3 -m pytest tests/test_auth.py"],
            "risk_points": ["index stale"],
        },
    )

    bundle = agent_protocol_bundle("fix auth", "src/auth.py::validate_token", Config(), tmp_path, protocol="codex")

    assert bundle["protocol"] == "codex"
    assert bundle["index_freshness"]["is_stale"] is True
    assert bundle["read_these_files"] == ["src/auth.py:1-20"]
    assert bundle["verify_commands"] == ["python3 -m pytest tests/test_auth.py"]


def test_resolve_symbol_uses_natural_language_alias_reasons(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import resolve_symbol

    hits = [
        {
            "id": "src/auth.py::login_handler",
            "metadata": {"file": "src/auth.py", "type": "function", "line_start": 1, "line_end": 8},
            "document": "POST /login endpoint authenticates users",
            "match_reasons": [],
        },
        {
            "id": "src/indexing.py::rebuild",
            "metadata": {"file": "src/indexing.py", "type": "function"},
            "document": "rebuild index",
            "match_reasons": [],
        },
    ]
    monkeypatch.setattr("indexer.retrieval.search_symbols", lambda *args, **kwargs: hits)

    result = resolve_symbol("login endpoint", Config(), tmp_path)

    assert result["status"] == "resolved"
    assert result["symbol"]["id"] == "src/auth.py::login_handler"
    assert "natural language alias match" in result["symbol"]["match_reasons"]


def test_vector_metadata_marks_entry_points():
    from indexer.ast_parser import ASTNode
    from indexer.vector_store import _build_meta

    node = ASTNode(
        id="src/api.py::login_handler",
        type="function",
        file="src/api.py",
        line_start=10,
        line_end=20,
        docstring="POST /login endpoint",
    )

    meta = _build_meta(node)

    assert meta["entry_point"] is True
    assert meta["entry_point_kind"] == "api"


def test_list_entry_points_reads_first_class_metadata(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import list_entry_points

    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={"src/api.py": FileEntry("sha256:x", "wiki/api.md", ["src/api.py::login_handler"])},
        ),
    )
    monkeypatch.setattr(
        "indexer.retrieval.get_by_ids",
        lambda ids, vector_store, repo_root: [
            {
                "id": "src/api.py::login_handler",
                "metadata": {"file": "src/api.py", "entry_point": True, "entry_point_kind": "api"},
                "document": "POST /login endpoint",
            }
        ],
    )

    result = list_entry_points(Config(), tmp_path)

    assert result["total"] == 1
    assert result["results"][0]["kind"] == "api"


def test_locate_from_error_uses_stack_trace_file_and_line(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import locate_from_error

    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={"src/auth.py": FileEntry("sha256:x", "wiki/auth.md", ["src/auth.py::validate_token"])},
        ),
    )
    node = {
        "id": "src/auth.py::validate_token",
        "metadata": {"file": "src/auth.py", "line_start": 40, "line_end": 55},
        "document": "validate token",
    }
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [node])
    monkeypatch.setattr("indexer.retrieval.search_symbols", lambda *args, **kwargs: [])

    result = locate_from_error('File "src/auth.py", line 44, in validate_token\nValueError: bad token', Config(), tmp_path)

    assert result["candidates"][0]["id"] == "src/auth.py::validate_token"
    assert "stack frame line inside symbol" in result["candidates"][0]["reasons"]


def test_locate_from_error_matches_http_path_to_entry_point(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import locate_from_error

    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={"src/api.py": FileEntry("sha256:x", "wiki/api.md", ["src/api.py::login_handler"])},
        ),
    )
    node = {
        "id": "src/api.py::login_handler",
        "metadata": {"file": "src/api.py", "line_start": 10, "line_end": 20, "entry_point": True},
        "document": "POST /login endpoint authenticates users",
    }
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [node])
    monkeypatch.setattr("indexer.retrieval.search_symbols", lambda *args, **kwargs: [])

    result = locate_from_error("POST /login returned 500", Config(), tmp_path)

    assert result["candidates"][0]["id"] == "src/api.py::login_handler"
    assert "http path match" in result["candidates"][0]["reasons"]


def test_post_edit_verify_maps_diff_to_symbols_tests_and_reindex(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import post_edit_verify

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "src" / "auth.py").write_text("def validate_token():\n    return True\n")
    (tmp_path / "tests" / "test_auth.py").write_text("def test_validate_token():\n    pass\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit="abc123",
            indexed_at="",
            files={
                "src/auth.py": FileEntry("sha256:x", "wiki/auth.md", ["src/auth.py::validate_token"]),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )
    node = {
        "id": "src/auth.py::validate_token",
        "metadata": {"file": "src/auth.py", "line_start": 1, "line_end": 4, "called_by": "[]", "calls": "[]"},
        "document": "validate token",
    }
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [node] if "src/auth.py::validate_token" in ids else [])
    monkeypatch.setattr("indexer.retrieval.get_index_status", lambda repo_root: {"is_stale": True, "reasons": ["indexed file hashes differ"]})

    diff = """diff --git a/src/auth.py b/src/auth.py
@@ -1,2 +1,3 @@
 def validate_token():
-    return True
+    return False
"""

    result = post_edit_verify(Config(), tmp_path, diff=diff)

    assert result["changed_files"] == ["src/auth.py"]
    assert result["changed_symbols"][0]["id"] == "src/auth.py::validate_token"
    assert "python3 -m pytest tests/test_auth.py" in result["verify_commands"]
    assert result["needs_reindex"] is True
    assert "Run repo-wiki run after verification" in result["checklist"][-1]


def test_diff_payload_size_guard_rejects_oversized_diff(monkeypatch):
    import indexer.rest_api as api

    monkeypatch.setattr(api, "MAX_DIFF_BYTES", 8)

    response = api._validate_diff_payload("x" * 9)

    assert response is not None
    assert response.status_code == 413


def test_stable_symbol_id_is_deterministic_and_metadata_includes_it():
    from indexer.ast_parser import ASTNode
    from indexer.retrieval import stable_symbol_id
    from indexer.vector_store import _build_meta

    node = ASTNode(
        id="src/auth.py::validate_token",
        type="function",
        file="src/auth.py",
        line_start=3,
        line_end=5,
        docstring="Validate token",
    )

    sid = stable_symbol_id(node.id, node.type, node.file, "def validate_token():")
    meta = _build_meta(node)

    assert sid == stable_symbol_id(node.id, node.type, node.file, "def validate_token():")
    assert sid.startswith("sym:")
    assert meta["stable_symbol_id"].startswith("sym:")


def test_change_set_combines_target_impact_tests_and_post_edit(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import change_set

    monkeypatch.setattr(
        "indexer.retrieval.impact_analysis",
        lambda symbol_id, cfg, repo_root, max_depth=2: {
            "symbol": {"id": symbol_id, "metadata": {"file": "src/auth.py"}},
            "direct_callers": [{"id": "src/api.py::login", "metadata": {"file": "src/api.py"}}],
            "direct_callees": [],
            "candidate_tests": [{"file": "tests/test_auth.py"}],
            "affected_files": ["src/auth.py", "src/api.py", "tests/test_auth.py"],
            "risk_points": ["Changed entry point"],
        },
    )
    monkeypatch.setattr(
        "indexer.retrieval.post_edit_verify",
        lambda cfg, repo_root, diff="", changed_files=None: {
            "changed_files": ["src/auth.py"],
            "changed_symbols": [{"id": "src/auth.py::validate_token", "file": "src/auth.py"}],
            "verify_commands": ["python3 -m pytest tests/test_auth.py"],
        },
    )

    result = change_set("fix auth", Config(), tmp_path, symbol_id="src/auth.py::validate_token", diff="diff")

    assert "src/auth.py" in result["must_change_files"]
    assert "src/api.py::login" in result["related_symbols"]
    assert "python3 -m pytest tests/test_auth.py" in result["verify_commands"]


def test_change_set_respects_max_results_and_summary(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import change_set

    monkeypatch.setattr(
        "indexer.retrieval.post_edit_verify",
        lambda *args, **kwargs: {
            "changed_files": [f"src/f{i}.py" for i in range(20)],
            "changed_symbols": [{"id": f"src/f{i}.py::fn", "file": f"src/f{i}.py"} for i in range(20)],
            "verify_commands": ["python3 -m pytest"],
            "candidate_tests": [],
            "risk_points": [],
        },
    )
    monkeypatch.setattr(
        "indexer.retrieval.impact_analysis",
        lambda *args, **kwargs: {
            "symbol": None,
            "direct_callers": [],
            "direct_callees": [],
            "candidate_tests": [],
            "affected_files": [],
            "risk_points": [],
        },
    )

    result = change_set("goal", Config(), tmp_path, diff="diff", max_results=5, include_details=False)

    assert result["summary"]["changed_file_count"] == 20
    assert len(result["must_change_files"]) == 5
    assert result["details_omitted"] is True


def test_coverage_map_links_tests_to_source_symbols(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import coverage_map

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_auth.py").write_text("from src.auth import validate_token\n\ndef test_validate_token(): pass\n")
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry("sha256:x", "wiki/auth.md", ["src/auth.py::validate_token"]),
                "tests/test_auth.py": FileEntry("sha256:y", "wiki/tests.md", ["tests/test_auth.py::test_validate_token"]),
            },
        ),
    )
    monkeypatch.setattr(
        "indexer.retrieval.get_by_ids",
        lambda ids, vector_store, repo_root: [
            {"id": i, "metadata": {"file": i.split("::")[0]}, "document": i}
            for i in ids
        ],
    )

    result = coverage_map(Config(), tmp_path, symbol_id="src/auth.py::validate_token")

    assert result["covered"] is True
    assert result["tests"][0]["file"] == "tests/test_auth.py"


def test_coverage_map_repo_wide_respects_max_results(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.manifest import FileEntry, Manifest, save_manifest
    from indexer.retrieval import coverage_map

    files = {
        f"src/f{i}.py": FileEntry("sha256:x", "wiki/src.md", [f"src/f{i}.py::fn"])
        for i in range(10)
    }
    save_manifest(tmp_path, Manifest(last_indexed_commit=None, indexed_at="", files=files))
    monkeypatch.setattr("indexer.retrieval.find_tests_for_symbol", lambda *args, **kwargs: [])

    result = coverage_map(Config(), tmp_path, max_results=3)

    assert result["total"] == 10
    assert len(result["symbols"]) == 3


def test_index_diff_report_compares_symbol_sets(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import index_diff_report

    before = [{"id": "src/a.py::old", "metadata": {"file": "src/a.py", "calls": "[]"}}]
    after = [
        {"id": "src/a.py::new", "metadata": {"file": "src/a.py", "calls": "[\"src/b.py::b\"]", "entry_point": True}},
    ]

    result = index_diff_report(Config(), tmp_path, before_nodes=before, after_nodes=after)

    assert result["added_symbols"] == ["src/a.py::new"]
    assert result["removed_symbols"] == ["src/a.py::old"]
    assert result["entry_point_changes"]["added"] == ["src/a.py::new"]
    assert result["call_graph_changes"]["added_edges"] == [["src/a.py::new", "src/b.py::b"]]


def test_cross_repo_graph_links_client_to_backend_route(monkeypatch, tmp_path):
    from indexer.retrieval import cross_repo_graph

    repos = {
        "frontend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": "src/api.ts::login", "metadata": {"file": "src/api.ts"}, "document": "fetch POST /login"}],
        },
        "backend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": "server/auth.py::login_handler", "metadata": {"file": "server/auth.py", "entry_point": True}, "document": "POST /login endpoint"}],
        },
    }

    result = cross_repo_graph(repos)

    assert result["edges"][0]["from_repo"] == "frontend"
    assert result["edges"][0]["to_repo"] == "backend"
    assert result["edges"][0]["kind"] == "http_path"


def test_cross_repo_graph_links_graphql_operation(tmp_path):
    from indexer.retrieval import cross_repo_graph

    repos = {
        "frontend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": "src/gql.ts::loadUser", "metadata": {"file": "src/gql.ts"}, "document": "query GetUser { user { id } }"}],
        },
        "backend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": "server/schema.py::resolve_user", "metadata": {"file": "server/schema.py"}, "document": "GraphQL resolver for GetUser"}],
        },
    }

    result = cross_repo_graph(repos)

    assert result["edges"][0]["kind"] == "graphql_operation"
    assert result["edges"][0]["operation"] == "GetUser"


def test_cross_repo_graph_respects_max_results(tmp_path):
    from indexer.retrieval import cross_repo_graph

    repos = {
        "frontend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": f"src/api.ts::call{i}", "metadata": {}, "document": "fetch POST /login"} for i in range(10)],
        },
        "backend": {
            "root": tmp_path,
            "config": object(),
            "nodes": [{"id": "server/auth.py::login_handler", "metadata": {}, "document": "POST /login endpoint"}],
        },
    }

    result = cross_repo_graph(repos, max_results=4)

    assert result["total"] == 10
    assert len(result["edges"]) == 4


def test_index_diff_report_detects_rename_by_stable_id(tmp_path):
    from indexer.config import Config
    from indexer.retrieval import index_diff_report

    before = [{"id": "src/a.py::old_name", "metadata": {"stable_symbol_id": "sym:abc"}}]
    after = [{"id": "src/b.py::new_name", "metadata": {"stable_symbol_id": "sym:abc"}}]

    result = index_diff_report(Config(), tmp_path, before_nodes=before, after_nodes=after)

    assert result["renamed_or_moved_symbols"] == [{
        "stable_symbol_id": "sym:abc",
        "before": "src/a.py::old_name",
        "after": "src/b.py::new_name",
    }]
    assert result["added_symbols"] == []
    assert result["removed_symbols"] == []


def test_agent_capabilities_manifest_lists_local_and_remote_tools():
    from indexer.retrieval import agent_capabilities_manifest

    manifest = agent_capabilities_manifest()

    assert manifest["local_and_remote"] is True
    assert "change_set_tool" in manifest["tools"]
    assert manifest["recommended_flow"][0] == "list_repos"
