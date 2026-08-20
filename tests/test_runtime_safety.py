from __future__ import annotations

import time

from starlette.testclient import TestClient


def test_task_store_returns_copies_and_keeps_running_tasks_during_cleanup():
    from indexer.task_store import TaskStore

    store = TaskStore()
    running = store.create("demo", "")
    store.update(running, status="running")
    finished = store.create("old", "")
    store.update(finished, status="completed")
    store.tasks[finished]["_finished_at"] = time.time() - store._TTL_SECONDS - 1

    copy = store.get(running)
    copy["status"] = "changed"
    store._cleanup()

    assert store.get(running)["status"] == "running"
    assert store.get(finished) is None


def test_registry_update_and_unregister_are_self_contained(tmp_path):
    from indexer.repo_registry import RepoRegistry

    repo = tmp_path / "repo"
    repo.mkdir()
    registry = RepoRegistry(tmp_path / "registry")
    registry.register(
        "demo",
        repo,
        branches=["main"],
        description="original",
        tags=["python"],
    )
    registry.update_meta("demo", description="updated")

    assert registry.get("demo")["description"] == "updated"
    assert registry.get("demo")["tags"] == ["python"]
    registry.unregister("demo")
    assert registry.get("demo") is None


def test_source_context_rejects_path_escape(tmp_path):
    from indexer.retrieval import get_source_context

    outside = tmp_path.parent / "outside.py"
    outside.write_text("secret = True\n")

    assert get_source_context("../outside.py", 1, 1, tmp_path).startswith("Access denied")


def test_register_rejects_invalid_url_before_background_work():
    from indexer.rest_api import create_app

    response = TestClient(create_app(repos={})).post(
        "/register",
        json={"name": "demo", "url": "file:///tmp/demo"},
    )

    assert response.status_code == 400
    assert "Unsupported URL scheme" in response.json()["error"]


def test_pre_commit_hook_uses_atomic_local_generation_command(tmp_path):
    from indexer.hooks import install_hook

    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    install_hook(tmp_path)

    hook = (tmp_path / ".git" / "hooks" / "pre-commit").read_text()
    assert "repo-wiki run --staged" in hook
    assert "local-only" not in hook
    assert "skip-deep" not in hook
