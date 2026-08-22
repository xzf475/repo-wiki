from __future__ import annotations

import subprocess
import threading
from pathlib import Path

from starlette.testclient import TestClient

from indexer.config import Config
from indexer.repository_index import IndexScope
from indexer.repository_service import RepositoryService, resolve_revision


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)


def _repository(tmp_path: Path) -> Path:
    root = tmp_path / "demo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "adapter@example.test")
    _git(root, "config", "user.name", "adapter test")
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / "src" / "auth.py").write_text(
        "def decode_token(token):\n"
        "    return token == 'ok'\n\n"
        "def validate_token(token):\n"
        "    return decode_token(token)\n"
    )
    (root / "src" / "api.py").write_text(
        "from auth import validate_token\n\n"
        "def login_handler(token):\n"
        "    \"\"\"POST /login endpoint.\"\"\"\n"
        "    return validate_token(token)\n"
    )
    (root / "tests" / "test_auth.py").write_text(
        "from src.auth import validate_token\n\n"
        "def test_validate_token():\n"
        "    assert validate_token('ok')\n"
    )
    _commit(root, "initial")
    return root


def _registered_rest_repo(monkeypatch, tmp_path: Path):
    from indexer import rest_api
    from indexer.repo_registry import RepoRegistry
    from indexer.task_store import TaskStore

    root = tmp_path / "repo"
    root.mkdir()
    registry = RepoRegistry(tmp_path / "registry")
    registry.register(
        "demo",
        root,
        url="https://example.test/demo.git",
        branches=["main"],
    )
    monkeypatch.setattr(rest_api, "registry", registry)
    monkeypatch.setattr(rest_api, "tasks", TaskStore())
    return rest_api, registry, root


def test_retrieval_and_service_return_the_same_generation_and_order(tmp_path: Path):
    from indexer.retrieval import search_code

    root = _repository(tmp_path)
    service = RepositoryService(root.name, root, "main", config=Config())
    sync = service.sync()

    direct = service.search("validate_token", retrieval="local")
    adapted = search_code(
        "validate_token",
        Config(),
        root,
        branch="main",
        explain=True,
    )

    assert direct["generation"] == adapted["generation"] == sync["sync"]["generation"]
    assert [item["id"] for item in direct["matches"]] == [
        item["id"] for item in adapted["matches"]
    ]


def test_rest_search_requires_explicit_branch_and_preserves_scope(monkeypatch, tmp_path: Path):
    from indexer import rest_api

    root = _repository(tmp_path)
    _git(root, "checkout", "-b", "feature")
    (root / "src" / "auth.py").write_text(
        "def feature_decode(token):\n"
        "    return token.startswith('feature:')\n\n"
        "def validate_token(token):\n"
        "    return feature_decode(token)\n"
    )
    _commit(root, "feature auth")
    _git(root, "checkout", "main")

    cfg = Config()
    main = RepositoryService("demo", root, "main", config=cfg)
    feature = RepositoryService("demo", root, "feature", config=cfg)
    main.sync()
    feature_sync = feature.sync()
    info = {"root": root, "config": cfg, "branches": ["main", "feature"]}
    monkeypatch.setattr(rest_api, "_resolve_repos", lambda repo: [("demo", info)])
    client = TestClient(rest_api.create_app())

    ambiguous = client.post("/search", json={
        "query": "validate_token",
        "repo": "demo",
        "retrieval": "local",
    })
    selected = client.post("/search", json={
        "query": "validate_token",
        "repo": "demo",
        "branch": "feature",
        "retrieval": "local",
    })

    assert ambiguous.status_code == 400
    assert selected.status_code == 200
    payload = selected.json()
    assert payload["matches"][0]["branch"] == "feature"
    assert payload["search_metrics"][0]["generation"] == feature_sync["sync"]["generation"]
    assert payload["index_status"][0]["current_branch"] == "feature"


def test_rest_local_repo_uses_current_branch_when_registry_has_no_branch(monkeypatch, tmp_path: Path):
    from indexer import rest_api

    root = _repository(tmp_path)
    cfg = Config()
    RepositoryService("demo", root, "main", config=cfg).sync()
    info = {"root": root, "config": cfg, "branches": []}
    monkeypatch.setattr(rest_api, "_resolve_repos", lambda repo: [("demo", info)])
    client = TestClient(rest_api.create_app())

    response = client.post("/search", json={
        "query": "validate_token",
        "repo": "demo",
        "retrieval": "local",
    })

    assert response.status_code == 200
    assert response.json()["search_metrics"][0]["branch"] == "main"


def test_rest_trace_rejects_unknown_branch(monkeypatch, tmp_path: Path):
    from indexer import rest_api

    root = _repository(tmp_path)
    info = {"root": root, "config": Config(), "branches": ["main"]}
    monkeypatch.setattr(rest_api, "_resolve_repos", lambda repo: [("demo", info)])
    client = TestClient(rest_api.create_app())

    response = client.post("/trace", json={
        "symbol_id": "src/auth.py::validate_token",
        "repo": "demo",
        "branch": "missing",
    })

    assert response.status_code == 400
    assert response.json()["repos"] == ["demo"]


def test_update_repo_and_sync_discovers_branch_with_repo_credentials(monkeypatch, tmp_path: Path):
    rest_api, registry, root = _registered_rest_repo(monkeypatch, tmp_path)

    def discover(_url, _pattern, cwd=None, **_kwargs):
        return ["test"] if cwd == root else []

    scheduled: list[str] = []
    completed = threading.Event()

    def run_all(_name, branches, _task_id, **_kwargs):
        scheduled.extend(branches)
        completed.set()

    monkeypatch.setattr(rest_api, "_discover_remote_branches", discover)
    monkeypatch.setattr(rest_api, "_run_all_branches", run_all)

    response = TestClient(rest_api.create_app()).post(
        "/api/repo/demo/sync",
        json={"branch_rule": "test", "enrich": False},
    )

    assert response.status_code == 200
    assert response.json()["branches"] == ["test"]
    assert completed.wait(1)
    assert scheduled == ["test"]
    assert registry.get("demo")["branches"] == ["test"]


def test_update_repo_and_sync_rejects_unmatched_rule_without_syncing_old_branches(
    monkeypatch,
    tmp_path: Path,
):
    rest_api, registry, _root = _registered_rest_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(rest_api, "_discover_remote_branches", lambda *_args, **_kwargs: [])

    scheduled = threading.Event()

    def run_all(*_args, **_kwargs):
        scheduled.set()

    monkeypatch.setattr(rest_api, "_run_all_branches", run_all)

    response = TestClient(rest_api.create_app()).post(
        "/api/repo/demo/sync",
        json={"branch_rule": "test", "enrich": False},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "no remote branches match pattern 'test'"
    assert registry.get("demo")["branch_rule"] == ""
    assert registry.get("demo")["branches"] == ["main"]
    assert not scheduled.wait(0.1)


def test_sync_all_rejects_unmatched_rule_instead_of_reusing_old_branches(
    monkeypatch,
    tmp_path: Path,
):
    rest_api, registry, _root = _registered_rest_repo(monkeypatch, tmp_path)
    registry.update_meta("demo", branch_rule="test")
    monkeypatch.setattr(rest_api, "_discover_remote_branches", lambda *_args, **_kwargs: [])
    scheduled = threading.Event()

    def run_all(*_args, **_kwargs):
        scheduled.set()

    monkeypatch.setattr(rest_api, "_run_all_branches", run_all)

    response = TestClient(rest_api.create_app()).post(
        "/sync-all",
        json={"name": "demo", "enrich": False},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "no remote branches match pattern 'test'"
    assert registry.get("demo")["branches"] == ["main"]
    assert not scheduled.wait(0.1)


def test_agent_context_and_diagnostics_read_repository_generation(tmp_path: Path):
    from indexer.retrieval import (
        diagnose_index,
        find_tests_for_symbol,
        get_edit_context,
        locate_from_error,
    )

    root = _repository(tmp_path)
    service = RepositoryService(root.name, root, "main", config=Config())
    service.sync()
    service.project()

    tests = find_tests_for_symbol("src/auth.py::validate_token", Config(), root)
    context = get_edit_context("src/auth.py::validate_token", Config(), root)
    located = locate_from_error(
        'File "src/auth.py", line 4, in validate_token\nValueError: bad token',
        Config(),
        root,
    )
    diagnostics = diagnose_index(root, Config())

    assert tests[0]["file"] == "tests/test_auth.py"
    assert context["symbol"]["id"] == "src/auth.py::validate_token"
    assert context["callees"][0]["id"] == "src/auth.py::decode_token"
    assert located["candidates"][0]["id"] == "src/auth.py::validate_token"
    assert diagnostics["healthy"] is True
    assert diagnostics["checks"]["repository_index"]["generation"] == 1


def test_branch_status_isolated_in_same_database(tmp_path: Path):
    root = _repository(tmp_path)
    _git(root, "branch", "feature")
    main = RepositoryService("demo", root, "main")
    feature = RepositoryService("demo", root, "feature")

    main.sync()
    feature.sync()

    main_status = main.index.inspect(IndexScope("demo", "main"))
    feature_status = feature.index.inspect(IndexScope("demo", "feature"))
    assert main_status.generation == feature_status.generation == 1
    assert main_status.tree_id == feature_status.tree_id


def test_sync_all_reconciles_index_scopes_removed_by_branch_rule(
    monkeypatch,
    tmp_path: Path,
):
    from indexer import rest_api
    from indexer.task_store import TaskStore

    root = _repository(tmp_path)
    _git(root, "branch", "feature")
    config = Config()
    RepositoryService("demo", root, "main", config=config).sync()
    RepositoryService("demo", root, "feature", config=config).sync()
    store = TaskStore()
    monkeypatch.setattr(rest_api, "tasks", store)
    monkeypatch.setattr(rest_api, "git_fetch_refs", lambda _root: None)
    task_id = store.create("demo", "")

    rest_api._run_all_branches(
        "demo",
        ["main"],
        task_id,
        root=root,
        enrich=False,
        _skip_lock=True,
    )

    task = store.get(task_id)
    assert task["status"] == "completed"
    assert task["result"]["removed_branches"] == ["feature"]
    assert RepositoryService(
        "demo", root, "feature", config=config
    ).index.inspect(IndexScope("demo", "feature")).exists is False


def test_remote_tracking_ref_wins_over_stale_local_branch(tmp_path: Path):
    root = _repository(tmp_path)
    main_tree = _git(root, "rev-parse", "main^{tree}")
    _git(root, "checkout", "-b", "remote-update")
    (root / "src" / "new_api.py").write_text("def remote_handler():\n    return True\n")
    _commit(root, "remote update")
    remote_commit = _git(root, "rev-parse", "HEAD")
    remote_tree = _git(root, "rev-parse", "HEAD^{tree}")
    _git(root, "checkout", "main")
    _git(root, "update-ref", "refs/remotes/origin/main", remote_commit)

    revision = resolve_revision(root, "main")
    report = RepositoryService("demo", root, "main").sync()

    assert revision == "refs/remotes/origin/main"
    assert report["sync"]["tree_id"] == remote_tree
    assert report["sync"]["tree_id"] != main_tree
