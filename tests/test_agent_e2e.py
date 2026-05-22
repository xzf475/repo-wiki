def test_agent_error_to_verify_flow_on_small_repo(monkeypatch, tmp_path):
    from indexer.ast_parser import parse_file
    from indexer.config import Config
    from indexer.indexing import cross_reference
    from indexer.manifest import FileEntry, Manifest, compute_hash, save_manifest
    from indexer.retrieval import change_set, locate_from_error, post_edit_verify

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    auth = tmp_path / "src" / "auth.py"
    api = tmp_path / "src" / "api.py"
    test_auth = tmp_path / "tests" / "test_auth.py"
    auth.write_text("def validate_token(token):\n    return token == 'ok'\n")
    api.write_text('def login_handler(token):\n    """POST /login endpoint"""\n    return validate_token(token)\n')
    test_auth.write_text("from src.auth import validate_token\n\ndef test_validate_token():\n    assert validate_token('ok')\n")

    nodes = []
    for path in (auth, api, test_auth):
        nodes.extend(parse_file(path, tmp_path))
    cross_reference(nodes)
    save_manifest(
        tmp_path,
        Manifest(
            last_indexed_commit=None,
            indexed_at="",
            files={
                "src/auth.py": FileEntry(compute_hash(auth), "wiki/src.md", [n.id for n in nodes if n.file == "src/auth.py"]),
                "src/api.py": FileEntry(compute_hash(api), "wiki/src.md", [n.id for n in nodes if n.file == "src/api.py"]),
                "tests/test_auth.py": FileEntry(compute_hash(test_auth), "wiki/tests.md", [n.id for n in nodes if n.file == "tests/test_auth.py"]),
            },
        ),
    )
    node_map = {
        n.id: {
            "id": n.id,
            "metadata": {
                "file": n.file,
                "line_start": n.line_start,
                "line_end": n.line_end,
                "type": n.type,
                "calls": __import__("json").dumps(n.calls),
                "called_by": __import__("json").dumps(n.called_by),
                "entry_point": n.id.endswith("::login_handler"),
                "entry_point_kind": "api" if n.id.endswith("::login_handler") else "",
            },
            "document": f"{n.id} {n.docstring or ''}",
        }
        for n in nodes
    }
    monkeypatch.setattr("indexer.retrieval.get_by_ids", lambda ids, vector_store, repo_root: [node_map[i] for i in ids if i in node_map])
    monkeypatch.setattr("indexer.retrieval.search_symbols", lambda *args, **kwargs: [])
    monkeypatch.setattr("indexer.retrieval.get_index_status", lambda repo_root: {"is_stale": False, "reasons": []})

    located = locate_from_error('File "src/auth.py", line 1, in validate_token\nValueError: bad token', Config(), tmp_path)
    assert located["candidates"][0]["id"] == "src/auth.py::validate_token"

    diff = """diff --git a/src/auth.py b/src/auth.py
@@ -1,2 +1,2 @@
 def validate_token(token):
-    return token == 'ok'
+    return bool(token)
"""
    verify = post_edit_verify(Config(), tmp_path, diff=diff)
    assert verify["changed_symbols"][0]["id"] == "src/auth.py::validate_token"
    assert "tests/test_auth.py" in [t["file"] for t in verify["candidate_tests"]]

    changes = change_set("fix token validation", Config(), tmp_path, symbol_id="src/auth.py::validate_token", diff=diff)
    assert "src/api.py" in changes["must_change_files"]
    assert "tests/test_auth.py" in changes["must_change_files"]
