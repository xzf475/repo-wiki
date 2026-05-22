def test_agent_capabilities_all_tools_have_schemas():
    from indexer.retrieval import agent_capabilities_manifest

    manifest = agent_capabilities_manifest()

    assert manifest["local_and_remote"] is True
    assert isinstance(manifest["tools"], dict)
    for name, spec in manifest["tools"].items():
        assert spec["input_schema"], name
        assert spec["output_schema"], name
        assert spec["example"], name
        assert "local" in spec["modes"] or "remote" in spec["modes"]


def test_core_tool_contract_top_level_keys(monkeypatch, tmp_path):
    from indexer.config import Config
    from indexer.retrieval import (
        agent_protocol_bundle,
        change_set,
        coverage_map,
        index_diff_report,
        post_edit_verify,
    )

    monkeypatch.setattr("indexer.retrieval.get_index_status", lambda repo_root: {"is_stale": False, "reasons": []})
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [])

    assert {"changed_files", "changed_symbols", "verify_commands"} <= set(post_edit_verify(Config(), tmp_path, changed_files=[]))
    assert {"must_change_files", "related_symbols", "verify_commands"} <= set(change_set("goal", Config(), tmp_path, changed_files=[]))
    assert {"symbols", "total", "index_status"} <= set(coverage_map(Config(), tmp_path))
    assert {"added_symbols", "removed_symbols", "call_graph_changes"} <= set(index_diff_report(Config(), tmp_path))

    monkeypatch.setattr(
        "indexer.retrieval.change_plan",
        lambda *args, **kwargs: {
            "index_status": {"is_stale": False},
            "read_these_files": [],
            "edit_targets": [],
            "verify_commands": [],
            "risk_points": [],
        },
    )
    assert {"read_these_files", "verify_commands", "index_freshness"} <= set(
        agent_protocol_bundle("goal", "src/a.py::fn", Config(), tmp_path)
    )


def test_agent_capabilities_endpoint_contract():
    from starlette.testclient import TestClient
    from indexer.rest_api import create_app

    client = TestClient(create_app(repos={}))
    response = client.get("/agent-capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["local_and_remote"] is True
    assert "post_edit_verify_tool" in payload["tools"]
    assert "json_schema" in payload


def test_agent_schema_endpoint_exports_machine_readable_contract():
    from starlette.testclient import TestClient
    from indexer.rest_api import create_app

    client = TestClient(create_app(repos={}))
    response = client.get("/agent-schema")

    assert response.status_code == 200
    payload = response.json()
    assert payload["openapi"] == "3.1.0"
    assert "/post-edit-verify" in payload["paths"]
    assert "AgentCapabilities" in payload["components"]["schemas"]


def test_stable_symbol_id_endpoint_contract():
    from starlette.testclient import TestClient
    from indexer.rest_api import create_app

    client = TestClient(create_app(repos={}))
    response = client.post(
        "/stable-symbol-id",
        json={"symbol_id": "src/auth.py::validate_token", "symbol_type": "function", "file_path": "src/auth.py"},
    )

    assert response.status_code == 200
    assert response.json()["stable_symbol_id"].startswith("sym:")


def test_post_edit_verify_endpoint_rejects_oversized_diff(monkeypatch):
    from starlette.testclient import TestClient
    import indexer.rest_api as api

    monkeypatch.setattr(api, "MAX_DIFF_BYTES", 8)
    client = TestClient(api.create_app(repos={}))
    response = client.post("/post-edit-verify", json={"repo": "missing", "diff": "x" * 9})

    assert response.status_code == 413


def test_agent_modules_expose_split_boundaries():
    import indexer.agent_context as agent_context
    import indexer.agent_diagnostics as agent_diagnostics
    import indexer.agent_diff as agent_diff
    import indexer.agent_graph as agent_graph
    import indexer.agent_protocol as agent_protocol

    assert agent_context.__all__
    assert "diagnose_index" in agent_diagnostics.__all__
    assert "post_edit_verify" in agent_diff.__all__
    assert "cross_repo_graph" in agent_graph.__all__
    assert "agent_schema" in agent_protocol.__all__


def test_agent_split_modules_own_function_bodies():
    import inspect
    import indexer.agent_context as agent_context
    import indexer.agent_diagnostics as agent_diagnostics
    import indexer.agent_diff as agent_diff
    import indexer.agent_graph as agent_graph

    assert inspect.getsourcefile(agent_context.resolve_symbol).endswith("agent_context.py")
    assert inspect.getsourcefile(agent_diagnostics.diagnose_index).endswith("agent_diagnostics.py")
    assert inspect.getsourcefile(agent_diff.post_edit_verify).endswith("agent_diff.py")
    assert inspect.getsourcefile(agent_graph.cross_repo_graph).endswith("agent_graph.py")
