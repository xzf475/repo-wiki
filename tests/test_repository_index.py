from __future__ import annotations

import sqlite3
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path

import pytest
from click.testing import CliRunner

import indexer.repository_index as repository_index_module
from indexer.cli import main as cli
from indexer.config import Config
from indexer.repository_projection import write_repository_projection
from indexer.repository_index import (
    IndexScope,
    RepositoryIndex,
    RepositoryIndexError,
    SearchRequest,
    SyncRequest,
)
from indexer.repository_store import SCHEMA_VERSION
from indexer.git_snapshot import STAGED_REVISION, WORKTREE_REVISION
from indexer.search_eval import SearchCase, evaluate_search


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _write_repository(root: Path) -> None:
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "repo-wiki@example.test")
    _git(root, "config", "user.name", "repo-wiki test")
    (root / "payments.py").write_text(
        'def create_order(amount):\n'
        '    """Create a payment order."""\n'
        '    return amount\n'
    )
    (root / "service.py").write_text(
        "from payments import create_order\n\n"
        "def checkout(amount):\n"
        "    return create_order(amount)\n"
    )
    _commit(root, "initial")


def _index(tmp_path: Path) -> RepositoryIndex:
    return RepositoryIndex(tmp_path / "repository-index.sqlite3")


class FakeEmbeddingProvider:
    model = "fake-semantic-v1"

    def __init__(self):
        self.document_batches: list[list[str]] = []
        self.query_calls: list[str] = []
        self.fail_documents = False
        self.fail_query = False

    def embed_documents(self, texts):
        if self.fail_documents:
            raise RuntimeError("document embedding unavailable")
        batch = list(texts)
        self.document_batches.append(batch)
        return [self._vector(text) for text in batch]

    def embed_query(self, text):
        if self.fail_query:
            raise RuntimeError("query embedding unavailable")
        self.query_calls.append(text)
        if "settle carried balance" in text.casefold():
            return [1.0, -1.0, 1.0, -1.0]
        return self._vector(text)

    @staticmethod
    def _vector(text: str):
        normalized = text.casefold()
        if "create_order" in normalized:
            return [1.0, -1.0, 1.0, -1.0]
        if "checkout" in normalized:
            return [-1.0, 1.0, 1.0, -1.0]
        return [1.0, 1.0, -1.0, -1.0]


def test_schema_upgrade_rebuilds_derived_v3_index(tmp_path: Path):
    database = tmp_path / "repository-index.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE files (legacy_value TEXT)")
        connection.execute("INSERT INTO files VALUES ('stale')")
        connection.execute("PRAGMA user_version = 3")

    RepositoryIndex(database)

    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert connection.execute("PRAGMA auto_vacuum").fetchone()[0] == 2
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        indexes = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }
    assert "files" not in tables
    assert {"parse_artifacts", "snapshots", "snapshot_changes"} <= tables
    assert "snapshot_changes_artifact_lookup_idx" in indexes


def test_newer_schema_is_rejected_without_modifying_database(tmp_path: Path):
    database = tmp_path / "repository-index.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE future_rows (value TEXT)")
        connection.execute("INSERT INTO future_rows VALUES ('preserve-me')")
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")

    with pytest.raises(RepositoryIndexError) as raised:
        RepositoryIndex(database)

    assert raised.value.code == "STORE_INCOMPATIBLE"
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == (
            SCHEMA_VERSION + 1
        )
        assert connection.execute("SELECT value FROM future_rows").fetchone()[0] == (
            "preserve-me"
        )


def test_schema_rebuild_compacts_derived_v3_storage(tmp_path: Path):
    database = tmp_path / "repository-index.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA auto_vacuum = INCREMENTAL")
        connection.execute("VACUUM")
        connection.execute("CREATE TABLE files (legacy_value TEXT)")
        connection.executemany(
            "INSERT INTO files VALUES (?)",
            [("x" * 10_000,) for _ in range(200)],
        )
        connection.execute("PRAGMA user_version = 3")
    before = database.stat().st_size

    RepositoryIndex(database)

    with sqlite3.connect(database) as connection:
        freelist = connection.execute("PRAGMA freelist_count").fetchone()[0]
    assert database.stat().st_size < before // 2
    assert freelist < 10


def test_sync_publishes_generation_and_inspect_reports_same_snapshot(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)

    report = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))
    status = index.inspect(IndexScope(repo="billing", branch="main"))

    assert report.status == "published"
    assert report.generation == 1
    assert report.tree_id == _git(repo, "rev-parse", "main^{tree}")
    assert set(report.changed_files) == {"payments.py", "service.py"}
    assert report.removed_files == ()
    assert report.parsed_blobs == 2
    assert status.exists is True
    assert status.generation == report.generation
    assert status.tree_id == report.tree_id
    assert status.files == 2
    assert status.symbols == 2


def test_symbols_project_current_generation_with_resolved_relations(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    symbols = index.symbols(scope)
    by_id = {symbol.component_id: symbol for symbol in symbols}

    assert tuple(by_id) == ("payments.py::create_order", "service.py::checkout")
    assert by_id["service.py::checkout"].calls == ("payments.py::create_order",)
    assert by_id["payments.py::create_order"].called_by == ("service.py::checkout",)
    assert index.symbols(scope, paths=("service.py",)) == (by_id["service.py::checkout"],)


def test_trace_reads_current_generation_call_graph_in_both_directions(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    down = index.trace(scope, "service.py::checkout", direction="down", max_depth=2)
    up = index.trace(scope, "payments.py::create_order", direction="up", max_depth=2)

    assert [symbol.component_id for symbol in down] == [
        "service.py::checkout",
        "payments.py::create_order",
    ]
    assert [symbol.component_id for symbol in up] == [
        "payments.py::create_order",
        "service.py::checkout",
    ]


def test_wiki_projection_is_rendered_from_published_generation(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    sync = index.sync(SyncRequest("billing", repo, "main", "main"))
    relation_builds = 0
    original_relation_rows = index._relation_rows

    def counted_relation_rows(connection, snapshot_id):
        nonlocal relation_builds
        relation_builds += 1
        return original_relation_rows(connection, snapshot_id)

    monkeypatch.setattr(index, "_relation_rows", counted_relation_rows)
    stale_page = repo / "wiki" / "stale.md"
    stale_page.parent.mkdir()
    stale_page.write_text("obsolete projection")

    report = write_repository_projection(repo, Config(), index, scope)

    assert report.generation == sync.generation
    assert report.tree_id == sync.tree_id
    assert report.files == 2
    assert report.symbols == 2
    assert sync.tree_id in (repo / "wiki" / "INDEX.md").read_text()
    assert "payments.py::create_order" in "\n".join(
        page.read_text() for page in (repo / "wiki").glob("*.md")
    )
    assert (repo / ".indexer" / "skills" / "codebase.md").exists()
    assert stale_page.exists() is False
    assert relation_builds == 1


def test_cli_run_and_status_use_repository_generation(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    runner = CliRunner()

    previous = Path.cwd()
    try:
        import os

        os.chdir(repo)
        run_result = runner.invoke(cli, ["run"], catch_exceptions=False)
        status_result = runner.invoke(cli, ["status"], catch_exceptions=False)
        maintain_result = runner.invoke(cli, ["maintain"], catch_exceptions=False)
    finally:
        os.chdir(previous)

    assert run_result.exit_code == 0
    assert "generation 1" in run_result.output
    assert "2 symbols" in run_result.output
    assert status_result.exit_code == 0
    assert "Generation:           1" in status_result.output
    assert "Stale files:          0" in status_result.output
    assert maintain_result.exit_code == 0
    assert "Reclaimed SQLite pages:" in maintain_result.output
    assert "SQLite integrity:        ok" in maintain_result.output


def test_unchanged_tree_is_constant_work_and_does_not_parse(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    parse_calls: list[str] = []

    def unexpected_parse(*args, **kwargs):
        parse_calls.append("called")
        raise AssertionError("unchanged sync must not parse")

    monkeypatch.setattr("indexer.repository_index.parse_file", unexpected_parse)
    report = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    assert report.status == "unchanged"
    assert report.changed_files == ()
    assert report.removed_files == ()
    assert report.parsed_blobs == 0
    assert report.reused_blobs == 0
    assert report.tree_entries_scanned == 0
    assert parse_calls == []


def test_incremental_sync_updates_and_removes_only_changed_paths(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    first = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    (repo / "payments.py").write_text(
        "def submit_invoice(amount):\n"
        "    return amount + 1\n"
    )
    (repo / "service.py").unlink()
    _commit(repo, "replace order flow")

    second = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    assert second.status == "published"
    assert second.generation == first.generation + 1
    assert second.changed_files == ("payments.py",)
    assert second.removed_files == ("service.py",)
    assert second.parsed_blobs == 1
    assert index.inspect(IndexScope("billing", "main")).files == 1
    assert index.search(SearchRequest(IndexScope("billing", "main"), "create_order")).matches == ()
    replacement = index.search(SearchRequest(IndexScope("billing", "main"), "submit_invoice"))
    assert replacement.matches[0].component_id == "payments.py::submit_invoice"


def test_branch_can_publish_a_previously_seen_tree_as_a_new_generation(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    original = (repo / "payments.py").read_text()
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    scope = IndexScope("billing", "main")

    first = index.sync(SyncRequest("billing", repo, "main", "main"))
    (repo / "payments.py").write_text("def replacement():\n    return True\n")
    _commit(repo, "replace payment flow")
    second = index.sync(SyncRequest("billing", repo, "main", "main"))
    (repo / "payments.py").write_text(original)
    _commit(repo, "restore payment flow")
    third = index.sync(SyncRequest("billing", repo, "main", "main"))

    assert (first.generation, second.generation, third.generation) == (1, 2, 3)
    assert third.tree_id == first.tree_id
    assert index.search(SearchRequest(scope, "create_order")).matches[0].component_id == (
        "payments.py::create_order"
    )
    with sqlite3.connect(database) as connection:
        head_snapshot, original_snapshot = connection.execute(
            """
                SELECT current.snapshot_id, original.id
            FROM branch_heads AS h
            JOIN generations AS current ON current.id = h.generation_id
            JOIN snapshots AS original
              ON original.repo_id = current.repo_id
             AND original.tree_id = ?
            WHERE h.repo_id = 'billing' AND h.branch = 'main'
            """,
            (first.tree_id,),
        ).fetchone()
    assert head_snapshot == original_snapshot


def test_same_blob_is_parsed_once_and_indexed_once_across_branches(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    index = _index(tmp_path)
    index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    def unexpected_parse(*args, **kwargs):
        raise AssertionError("content-addressed artifact should be reused")

    monkeypatch.setattr("indexer.repository_index.parse_file", unexpected_parse)
    report = index.sync(SyncRequest(repo="billing", root=repo, branch="feature", revision="feature"))

    assert report.status == "published"
    assert report.parsed_blobs == 0
    assert report.reused_blobs == 2
    assert index.inspect(IndexScope("billing", "feature")).symbols == 2
    with sqlite3.connect(tmp_path / "repository-index.sqlite3") as connection:
        artifacts = int(connection.execute(
            "SELECT COUNT(*) FROM parse_artifacts"
        ).fetchone()[0])
        artifact_symbols = int(connection.execute(
            "SELECT COUNT(*) FROM artifact_symbols"
        ).fetchone()[0])
        artifact_documents = int(connection.execute(
            "SELECT COUNT(*) FROM artifact_documents"
        ).fetchone()[0])
        snapshots = int(connection.execute(
            "SELECT COUNT(*) FROM snapshots"
        ).fetchone()[0])
        snapshot_changes = int(connection.execute(
            "SELECT COUNT(*) FROM snapshot_changes"
        ).fetchone()[0])
    assert artifacts == 2
    assert artifact_symbols == 2
    assert artifact_documents == 2
    assert snapshots == 1
    assert snapshot_changes == 2


def test_identical_branch_snapshots_publish_idempotently_under_concurrency(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    database = tmp_path / "repository-index.sqlite3"

    def synchronize(branch: str):
        return RepositoryIndex(database).sync(SyncRequest(
            "billing", repo, branch, branch
        ))

    with ThreadPoolExecutor(max_workers=2) as executor:
        reports = list(executor.map(synchronize, ("main", "feature")))

    assert {report.branch for report in reports} == {"main", "feature"}
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM snapshots"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM snapshot_changes"
        ).fetchone()[0] == 2


def test_sync_reports_retryable_conflict_if_reused_snapshot_is_reclaimed(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    database = tmp_path / "repository-index.sqlite3"
    owner = RepositoryIndex(database)
    owner.sync(SyncRequest("billing", repo, "main", "main"))
    feature = RepositoryIndex(database)
    original_publish = feature._publish_generation

    def reclaim_then_publish(**kwargs):
        owner.reconcile_branches("billing", ())
        return original_publish(**kwargs)

    monkeypatch.setattr(feature, "_publish_generation", reclaim_then_publish)

    with pytest.raises(RepositoryIndexError) as raised:
        feature.sync(SyncRequest("billing", repo, "feature", "feature"))

    assert raised.value.code == "SYNC_CONFLICT"
    assert raised.value.retryable is True


def test_sync_reports_retryable_conflict_if_overlay_base_is_reclaimed(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    (repo / "payments.py").write_text("def feature_order():\n    return True\n")
    _commit(repo, "feature payment")
    _git(repo, "checkout", "main")
    database = tmp_path / "repository-index.sqlite3"
    owner = RepositoryIndex(database)
    owner.sync(SyncRequest("billing", repo, "main", "main"))
    feature = RepositoryIndex(database)
    original_publish = feature._publish_generation

    def reclaim_then_publish(**kwargs):
        owner.reconcile_branches("billing", ())
        return original_publish(**kwargs)

    monkeypatch.setattr(feature, "_publish_generation", reclaim_then_publish)

    with pytest.raises(RepositoryIndexError) as raised:
        feature.sync(SyncRequest("billing", repo, "feature", "feature"))

    assert raised.value.code == "SYNC_CONFLICT"
    assert raised.value.retryable is True


def test_sync_reports_retryable_conflict_if_reused_artifact_is_reclaimed(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    _git(repo, "mv", "payments.py", "orders.py")
    (repo / "service.py").unlink()
    _commit(repo, "retain only renamed payment module")
    _git(repo, "checkout", "main")
    database = tmp_path / "repository-index.sqlite3"
    owner = RepositoryIndex(database)
    owner.sync(SyncRequest("billing", repo, "main", "main"))
    feature = RepositoryIndex(database)
    original_publish = feature._publish_generation

    def reclaim_then_publish(**kwargs):
        owner.reconcile_branches("billing", ())
        return original_publish(**kwargs)

    monkeypatch.setattr(feature, "_publish_generation", reclaim_then_publish)

    with pytest.raises(RepositoryIndexError) as raised:
        feature.sync(SyncRequest("billing", repo, "feature", "feature"))

    assert raised.value.code == "SYNC_CONFLICT"
    assert raised.value.retryable is True


def test_near_identical_branch_stores_only_snapshot_overlay(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    (repo / "payments.py").write_text("def feature_order():\n    return True\n")
    _commit(repo, "feature payment")
    _git(repo, "checkout", "main")

    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))
    report = index.sync(SyncRequest("billing", repo, "feature", "feature"))

    assert report.parsed_blobs == 1
    assert report.reused_blobs == 1
    with sqlite3.connect(database) as connection:
        feature_snapshot = connection.execute(
            """
            SELECT s.id, s.base_snapshot_id
            FROM branch_heads AS h
            JOIN generations AS g ON g.id = h.generation_id
            JOIN snapshots AS s ON s.id = g.snapshot_id
            WHERE h.repo_id = 'billing' AND h.branch = 'feature'
            """
        ).fetchone()
        overlay_rows = int(connection.execute(
            "SELECT COUNT(*) FROM snapshot_changes WHERE snapshot_id = ?",
            (feature_snapshot[0],),
        ).fetchone()[0])
        documents = int(connection.execute(
            "SELECT COUNT(*) FROM artifact_documents"
        ).fetchone()[0])
        fts_documents = int(connection.execute(
            "SELECT COUNT(*) FROM artifact_documents_fts"
        ).fetchone()[0])

    assert feature_snapshot[1] is not None
    assert overlay_rows == 1
    assert documents == 3
    assert fts_documents == 3
    assert index.search(SearchRequest(
        IndexScope("billing", "main"),
        "feature_order",
    )).matches == ()
    assert index.search(SearchRequest(
        IndexScope("billing", "feature"),
        "feature_order",
    )).matches[0].component_id == "payments.py::feature_order"


def test_generation_retention_keeps_delta_chain_without_full_rewrite(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))

    for revision in range(1, 5):
        (repo / "payments.py").write_text(
            f"def create_order(amount):\n    return amount + {revision}\n"
        )
        _commit(repo, f"payment revision {revision}")
        index.sync(SyncRequest("billing", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        snapshots = connection.execute(
            """
            SELECT s.id, s.base_snapshot_id, s.depth,
                   (SELECT COUNT(*) FROM snapshot_changes AS sc
                    WHERE sc.snapshot_id = s.id) AS changes
            FROM snapshots AS s
            WHERE s.repo_id = 'billing'
            ORDER BY s.id
            """
        ).fetchall()
        generations = connection.execute(
            "SELECT COUNT(*) FROM generations WHERE repo_id = 'billing'"
        ).fetchone()[0]

    assert generations == 2
    assert [row[2] for row in snapshots] == [0, 1, 2, 3, 4]
    assert [row[3] for row in snapshots] == [2, 1, 1, 1, 1]
    assert index.inspect(IndexScope("billing", "main")).files == 2


def test_overlay_depth_checkpoint_reclaims_detached_chain(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr("indexer.repository_index.MAX_SNAPSHOT_DEPTH", 4)
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))

    for revision in range(1, 6):
        (repo / "payments.py").write_text(
            f"def create_order(amount):\n    return amount + {revision}\n"
        )
        _commit(repo, f"payment revision {revision}")
        index.sync(SyncRequest("billing", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        snapshots = connection.execute(
            """
            SELECT s.depth,
                   (SELECT COUNT(*) FROM snapshot_changes AS sc
                    WHERE sc.snapshot_id = s.id) AS changes
            FROM snapshots AS s
            WHERE s.repo_id = 'billing'
            ORDER BY s.depth
            """
        ).fetchall()

    assert snapshots == [(0, 2), (1, 1)]
    assert index.inspect(IndexScope("billing", "main")).files == 2


def test_relation_cache_is_lazy_and_shared_by_identical_snapshots(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    main = IndexScope("billing", "main")
    feature = IndexScope("billing", "feature")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    index.sync(SyncRequest("billing", repo, "feature", "feature"))

    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM snapshot_relations"
        ).fetchone()[0] == 0

    assert index.trace(main, "service.py::checkout")[1].component_id == (
        "payments.py::create_order"
    )
    with sqlite3.connect(database) as connection:
        cached_after_main = int(connection.execute(
            "SELECT COUNT(*) FROM snapshot_relations"
        ).fetchone()[0])
        states_after_main = int(connection.execute(
            "SELECT COUNT(*) FROM relation_cache_states"
        ).fetchone()[0])

    assert index.trace(feature, "service.py::checkout")[1].component_id == (
        "payments.py::create_order"
    )
    with sqlite3.connect(database) as connection:
        cached_after_feature = int(connection.execute(
            "SELECT COUNT(*) FROM snapshot_relations"
        ).fetchone()[0])
        states_after_feature = int(connection.execute(
            "SELECT COUNT(*) FROM relation_cache_states"
        ).fetchone()[0])

    assert cached_after_main == cached_after_feature == 1
    assert states_after_main == states_after_feature == 1


def test_search_retries_relation_cache_when_head_changes(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "HEAD~0"))
    (repo / "README.md").write_text("new tree\n")
    _commit(repo, "non-source tree change")

    original = index._ensure_relation_cache
    advanced = False

    def ensure_then_advance(snapshot_id: int):
        nonlocal advanced
        cached = original(snapshot_id)
        if not advanced:
            advanced = True
            index.sync(SyncRequest("billing", repo, "main", "main"))
        return cached

    monkeypatch.setattr(index, "_ensure_relation_cache", ensure_then_advance)

    result = index.search(SearchRequest(scope, "create_order"))

    assert result.generation == 2
    assert [hit.component_id for hit in result.related] == ["service.py::checkout"]


@pytest.mark.parametrize("operation", ("symbols", "trace"))
def test_structural_reads_retry_relation_cache_when_head_changes(
    operation: str,
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "HEAD~0"))
    (repo / "README.md").write_text("new tree\n")
    _commit(repo, "non-source tree change")
    original = index._ensure_relation_cache
    advanced = False

    def ensure_then_advance(snapshot_id: int):
        nonlocal advanced
        cached = original(snapshot_id)
        if not advanced:
            advanced = True
            index.sync(SyncRequest("billing", repo, "main", "main"))
        return cached

    monkeypatch.setattr(index, "_ensure_relation_cache", ensure_then_advance)

    if operation == "symbols":
        records = index.symbols(scope, component_ids=("payments.py::create_order",))
        assert records[0].called_by == ("service.py::checkout",)
    else:
        records = index.trace(scope, "service.py::checkout")
        assert [record.component_id for record in records] == [
            "service.py::checkout",
            "payments.py::create_order",
        ]


def test_relation_cache_ignores_snapshot_reclaimed_before_cache_write(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    (repo / "payments.py").write_text("def feature_order():\n    return True\n")
    _commit(repo, "feature payment")
    _git(repo, "checkout", "main")
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))
    with sqlite3.connect(database) as connection:
        reclaimed_snapshot_id = connection.execute(
            "SELECT snapshot_id FROM generations WHERE branch = 'main'"
        ).fetchone()[0]
    index.sync(SyncRequest("billing", repo, "feature", "feature"))
    index.reconcile_branches("billing", ("feature",))

    assert index._ensure_relation_cache(reclaimed_snapshot_id) is False


def test_blob_artifact_survives_rename_without_stale_component_ids(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    _git(repo, "mv", "payments.py", "orders.py")
    (repo / "service.py").write_text(
        "from orders import create_order\n\n"
        "def checkout(amount):\n"
        "    return create_order(amount)\n"
    )
    _commit(repo, "rename payment module")

    report = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))
    result = index.search(SearchRequest(IndexScope("billing", "main"), "create_order"))

    assert set(report.changed_files) == {"orders.py", "service.py"}
    assert report.removed_files == ("payments.py",)
    assert report.parsed_blobs == 1
    assert report.reused_blobs == 1
    assert result.matches[0].component_id == "orders.py::create_order"
    assert [hit.component_id for hit in result.related] == ["service.py::checkout"]
    assert all("payments.py::" not in hit.component_id for hit in (*result.matches, *result.related))


def test_non_source_tree_change_publishes_snapshot_without_parsing(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    first = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))
    (repo / "README.md").write_text("new documentation\n")
    _commit(repo, "docs")

    def unexpected_parse(*args, **kwargs):
        raise AssertionError("non-source changes must not parse")

    monkeypatch.setattr("indexer.repository_index.parse_file", unexpected_parse)
    second = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    assert second.status == "published"
    assert second.generation == first.generation + 1
    assert second.changed_files == ()
    assert second.removed_files == ()
    assert second.parsed_blobs == 0
    assert second.tree_entries_scanned == 1
    assert index.inspect(IndexScope("billing", "main")).symbols == 2
    with sqlite3.connect(tmp_path / "repository-index.sqlite3") as connection:
        snapshots = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        head_snapshot = connection.execute(
            """
            SELECT g.snapshot_id
            FROM branch_heads AS h
            JOIN generations AS g ON g.id = h.generation_id
            WHERE h.repo_id = 'billing' AND h.branch = 'main'
            """
        ).fetchone()[0]
        first_snapshot = connection.execute(
            "SELECT snapshot_id FROM generations WHERE generation = 1"
        ).fetchone()[0]
    assert snapshots == 1
    assert head_snapshot == first_snapshot


def test_staged_revision_captures_index_without_changing_git_state(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    (repo / "payments.py").write_text("def staged_only():\n    return True\n")
    (repo / "wiki").mkdir()
    (repo / "wiki" / "INDEX.md").write_text("generated projection")
    _git(repo, "add", "payments.py")
    _git(repo, "add", "wiki/INDEX.md")
    staged_before = _git(repo, "diff", "--cached", "--name-only")
    objects_before = _git(repo, "count-objects", "-v")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(
        "billing",
        repo,
        "main",
        STAGED_REVISION,
    ))

    assert report.status == "published"
    assert index.search(SearchRequest(
        IndexScope("billing", "main"),
        "staged_only",
    )).matches[0].component_id == "payments.py::staged_only"
    assert _git(repo, "diff", "--cached", "--name-only") == staged_before
    assert _git(repo, "count-objects", "-v") == objects_before


def test_worktree_revision_captures_unstaged_and_untracked_without_staging(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    (repo / "payments.py").write_text("def unstaged_only():\n    return True\n")
    (repo / "new_module.py").write_text("def untracked_symbol():\n    return True\n")
    objects_before = _git(repo, "count-objects", "-v")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(
        "billing",
        repo,
        "worktree",
        WORKTREE_REVISION,
    ))

    assert set(report.changed_files) == {"new_module.py", "payments.py", "service.py"}
    assert index.search(SearchRequest(
        IndexScope("billing", "worktree"),
        "unstaged_only",
    )).matches[0].component_id == "payments.py::unstaged_only"
    assert index.search(SearchRequest(
        IndexScope("billing", "worktree"),
        "untracked_symbol",
    )).matches[0].component_id == "new_module.py::untracked_symbol"
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert "new_module.py" in _git(repo, "status", "--short")
    assert _git(repo, "count-objects", "-v") == objects_before

    (repo / "payments.py").write_text("def unstaged_again():\n    return True\n")
    second = index.sync(SyncRequest(
        "billing",
        repo,
        "worktree",
        WORKTREE_REVISION,
    ))

    assert second.changed_files == ("payments.py",)
    assert second.tree_entries_scanned == 1
    assert _git(repo, "count-objects", "-v") == objects_before

    (repo / "wiki").mkdir()
    (repo / "wiki" / "INDEX.md").write_text("generated projection changed")
    (repo / ".indexer" / "skills").mkdir(parents=True)
    (repo / ".indexer" / "skills" / "codebase.md").write_text("generated skill changed")
    projection_only = index.sync(SyncRequest(
        "billing",
        repo,
        "worktree",
        WORKTREE_REVISION,
    ))

    assert projection_only.status == "unchanged"
    assert projection_only.generation == second.generation

    maintenance = index.maintain(retain_generations=1)
    (repo / "service.py").write_text("def worktree_service():\n    return True\n")
    after_maintenance = index.sync(SyncRequest(
        "billing",
        repo,
        "worktree",
        WORKTREE_REVISION,
    ))

    assert maintenance.integrity.ok is True
    assert after_maintenance.changed_files == ("service.py",)


def test_maintenance_prunes_synthetic_objects_after_last_branch_is_removed(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    (repo / "payments.py").write_text("def worktree_only():\n    return True\n")
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "worktree", WORKTREE_REVISION))
    object_root = repo / ".indexer" / "state" / "git-objects"
    before = sum(path.is_file() for path in object_root.rglob("*"))

    index.reconcile_branches("billing", ())
    maintenance = index.maintain()
    after = sum(path.is_file() for path in object_root.rglob("*"))

    assert before > 0
    assert maintenance.deleted_snapshot_objects > 0
    assert after == 0


def test_maintenance_preserves_inflight_worktree_snapshot(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))
    (repo / "payments.py").write_text("def worktree_one():\n    return True\n")
    original_prepare = index._prepare_artifacts
    prepared = threading.Event()
    release = threading.Event()

    def prepare_then_wait(snapshot, entries):
        result = original_prepare(snapshot, entries)
        prepared.set()
        assert release.wait(5)
        return result

    monkeypatch.setattr(index, "_prepare_artifacts", prepare_then_wait)
    with ThreadPoolExecutor(max_workers=1) as executor:
        sync_future = executor.submit(
            index.sync,
            SyncRequest("billing", repo, "worktree", WORKTREE_REVISION),
        )
        assert prepared.wait(5)
        maintenance = RepositoryIndex(database).maintain()
        release.set()
        first = sync_future.result()

    assert maintenance.integrity.ok is True
    assert first.generation == 1
    monkeypatch.setattr(index, "_prepare_artifacts", original_prepare)
    (repo / "payments.py").write_text("def worktree_two():\n    return True\n")
    second = index.sync(SyncRequest(
        "billing",
        repo,
        "worktree",
        WORKTREE_REVISION,
    ))
    assert second.generation == 2
    lease_root = repo / ".indexer" / "state" / "git-object-leases"
    assert not any(lease_root.iterdir())


def test_maintenance_reclaims_multiple_free_pages(tmp_path: Path):
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    payload = "x" * 10_000
    with sqlite3.connect(database) as connection:
        connection.executemany(
            """
            INSERT INTO parse_artifacts(
                artifact_id, blob_id, parser_version, context_hash,
                payload_json, created_at
            ) VALUES (?, ?, 'test', 'test', ?, 'now')
            """,
            [
                (f"artifact-{number}", f"blob-{number}", payload)
                for number in range(300)
            ],
        )
        connection.commit()

    report = index.maintain()

    assert report.deleted_artifacts == 300
    assert report.reclaimed_pages > 1


def test_parse_failure_does_not_advance_visible_generation(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    first = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    (repo / "payments.py").write_text("def broken(:\n")
    _commit(repo, "broken")

    with pytest.raises(RepositoryIndexError) as raised:
        index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    assert raised.value.code == "PARSE_FAILED"
    assert index.inspect(IndexScope("billing", "main")).generation == first.generation
    result = index.search(SearchRequest(IndexScope("billing", "main"), "create_order"))
    assert result.matches[0].component_id == "payments.py::create_order"


def test_valid_source_without_symbols_is_not_treated_as_parse_failure(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "settings.py").write_text("DEFAULT_TIMEOUT = 30\n")
    _commit(repo, "settings")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(repo="settings", root=repo, branch="main", revision="main"))
    status = index.inspect(IndexScope("settings", "main"))

    assert report.status == "published"
    assert status.files == 1
    assert status.symbols == 0


def test_tree_sitter_syntax_error_is_rejected(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "broken.js").write_text("function broken( {\n")
    _commit(repo, "broken javascript")

    index = _index(tmp_path)
    with pytest.raises(RepositoryIndexError) as raised:
        index.sync(SyncRequest(repo="web", root=repo, branch="main", revision="main"))

    assert raised.value.code == "PARSE_FAILED"
    assert index.inspect(IndexScope("web", "main")).exists is False


def test_typescript_import_type_array_in_generic_publishes(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "issue-pool.ts").write_text(
        "declare function get<T>(path: string): T;\n"
        "export function releaseSummary() {\n"
        "  return get<import('../types').IssuePoolReleaseSummary[]>(\n"
        "    '/release-summary',\n"
        "  );\n"
        "}\n"
    )
    _commit(repo, "valid typescript import type")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(repo="web", root=repo, branch="main", revision="main"))
    status = index.inspect(IndexScope("web", "main"))

    assert report.status == "published"
    assert status.files == 1
    assert status.symbols == 1


def test_tsx_typeof_import_in_zero_arg_generic_publishes(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "UserCoinGrantPage.test.tsx").write_text(
        "vi.mock('@/services/adminApi', async (importOriginal) => ({\n"
        "  ...(await importOriginal<typeof import('@/services/adminApi')>()),\n"
        "}));\n"
    )
    _commit(repo, "valid tsx typeof import type")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(repo="web", root=repo, branch="main", revision="main"))
    status = index.inspect(IndexScope("web", "main"))

    assert report.status == "published"
    assert status.files == 1


def test_modern_typescript_type_only_syntax_publishes(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "api.ts").write_text(
        "declare function get<T>(path: string): T;\n"
        "export type * as Types from './types';\n"
        "type ConfigKey = keyof import('./types').Config;\n"
        "export function settings() {\n"
        "  return get<import('./types').Settings>('/settings');\n"
        "}\n"
    )
    _commit(repo, "modern typescript type syntax")

    index = _index(tmp_path)
    report = index.sync(SyncRequest(repo="web", root=repo, branch="main", revision="main"))
    status = index.inspect(IndexScope("web", "main"))

    assert report.status == "published"
    assert status.files == 1
    assert status.symbols == 1


def test_typescript_import_type_repair_does_not_hide_other_errors(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "broken.ts").write_text(
        "declare function get<T>(path: string): T;\n"
        "const releases = get<import('../types').Release[]>('/releases');\n"
        "function broken( {\n"
    )
    _commit(repo, "broken typescript")

    index = _index(tmp_path)
    with pytest.raises(RepositoryIndexError) as raised:
        index.sync(SyncRequest(repo="web", root=repo, branch="main", revision="main"))

    assert raised.value.code == "PARSE_FAILED"
    assert index.inspect(IndexScope("web", "main")).exists is False


def test_transaction_failure_rolls_back_materialized_state(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    first = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    (repo / "payments.py").write_text("def replacement():\n    return True\n")
    _commit(repo, "replacement")

    def fail_artifact_publish(*args, **kwargs):
        raise RuntimeError("artifact invariant failed")

    monkeypatch.setattr(index, "_insert_artifact_records", fail_artifact_publish)
    with pytest.raises(RepositoryIndexError) as raised:
        index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    assert raised.value.code == "INVARIANT_VIOLATION"
    assert index.inspect(IndexScope("billing", "main")).generation == first.generation
    assert index.search(SearchRequest(IndexScope("billing", "main"), "replacement")).matches == ()
    old = index.search(SearchRequest(IndexScope("billing", "main"), "create_order"))
    assert old.matches[0].component_id == "payments.py::create_order"


def test_search_combines_exact_and_fts_and_separates_related_symbols(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    report = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    exact = index.search(SearchRequest(IndexScope("billing", "main"), "create_order"))
    path = index.search(SearchRequest(IndexScope("billing", "main"), "payments"))
    lexical = index.search(SearchRequest(IndexScope("billing", "main"), "payment order"))

    assert exact.generation == report.generation
    assert exact.tree_id == report.tree_id
    assert exact.retrieval == "local"
    assert exact.degradations == ()
    assert exact.matches[0].component_id == "payments.py::create_order"
    assert exact.matches[0].score_breakdown["exact"] > 0
    assert [hit.component_id for hit in exact.related] == ["service.py::checkout"]
    assert path.matches[0].component_id == "payments.py::create_order"
    assert path.matches[0].score_breakdown["exact"] > 0
    assert lexical.matches[0].component_id == "payments.py::create_order"
    assert lexical.matches[0].score_breakdown["lexical"] > 0


def test_search_without_matches_does_not_materialize_relation_cache(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    result = index.search(SearchRequest(scope, "definitely_missing_symbol"))

    assert result.matches == ()
    assert result.related == ()
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM relation_cache_states"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM snapshot_relations"
        ).fetchone()[0] == 0


def test_path_substring_match_does_not_hide_lexical_results(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "service_helpers.py").write_text("def noop():\n    return None\n")
    (repo / "billing.py").write_text(
        "def reconcile():\n"
        "    \"\"\"Critical service workflow.\"\"\"\n"
        "    return True\n"
    )
    _commit(repo, "search corpus")
    index = _index(tmp_path)
    scope = IndexScope("search", "main")
    index.sync(SyncRequest("search", repo, "main", "main"))

    result = index.search(SearchRequest(scope, "service", related_limit=0))

    assert "billing.py::reconcile" in {
        match.component_id for match in result.matches
    }


def test_ambiguous_global_calls_resolve_only_through_imports(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    for number in range(40):
        (repo / f"target_{number}.py").write_text(
            f"def helper():\n    return {number}\n"
        )
    (repo / "caller.py").write_text(
        "from target_7 import helper\n\n"
        "def run():\n"
        "    return helper()\n"
    )
    _commit(repo, "ambiguous relation corpus")
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    scope = IndexScope("relations", "main")
    index.sync(SyncRequest("relations", repo, "main", "main"))

    traced = index.trace(scope, "caller.py::run")

    assert [record.component_id for record in traced] == [
        "caller.py::run",
        "target_7.py::helper",
    ]
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM snapshot_relations"
        ).fetchone()[0] == 1


def test_related_candidates_batch_neighbor_lookup(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    for number in range(30):
        (repo / f"module_{number}.py").write_text(
            f"def item_{number}():\n"
            "    \"\"\"shared retrieval marker\"\"\"\n"
            f"    return {number}\n"
        )
    _commit(repo, "related query corpus")
    index = _index(tmp_path)
    scope = IndexScope("related", "main")
    index.sync(SyncRequest("related", repo, "main", "main"))
    matches = index.search(SearchRequest(
        scope,
        "shared retrieval marker",
        limit=30,
        related_limit=0,
    )).matches
    head = index._read_head(scope)
    assert head is not None
    assert index._ensure_relation_cache(head.snapshot_id) is True
    statements: list[str] = []

    with index._store.transaction() as connection:
        connection.set_trace_callback(statements.append)
        index._related_candidates(connection, head.snapshot_id, matches, 30)

    neighbor_queries = [
        statement for statement in statements
        if "FROM snapshot_relations" in statement
    ]
    assert len(neighbor_queries) == 1


def test_relation_cache_build_does_not_hold_sqlite_writer_lock(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    syncing_index = RepositoryIndex(database)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    (repo / "payments.py").write_text("def revised_order():\n    return True\n")
    _commit(repo, "revised source")
    original_relation_rows = index._relation_rows
    relation_started = threading.Event()
    release_relation = threading.Event()
    calls = 0

    def blocked_relation_rows(connection, snapshot_id):
        nonlocal calls
        calls += 1
        if calls == 1:
            relation_started.set()
            assert release_relation.wait(5)
        return original_relation_rows(connection, snapshot_id)

    monkeypatch.setattr(index, "_relation_rows", blocked_relation_rows)
    sync_blocked = False
    with ThreadPoolExecutor(max_workers=2) as executor:
        relation_future = executor.submit(index.symbols, scope)
        assert relation_started.wait(5)
        sync_future = executor.submit(
            syncing_index.sync,
            SyncRequest("billing", repo, "main", "main"),
        )
        try:
            sync_report = sync_future.result(timeout=1)
        except FutureTimeoutError:
            sync_blocked = True
            sync_report = None
        finally:
            release_relation.set()
        relation_future.result()
        if sync_report is None:
            sync_future.result()

    assert sync_blocked is False
    assert sync_report is not None
    assert sync_report.generation == 2


def test_relation_cache_lock_timeout_is_reported_as_retryable_store_busy(
    monkeypatch,
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    original_connect = index._store.connect

    def quick_timeout_connection():
        connection = original_connect()
        connection.execute("PRAGMA busy_timeout = 1")
        return connection

    monkeypatch.setattr(index._store, "connect", quick_timeout_connection)
    blocker = sqlite3.connect(database, isolation_level=None)
    blocker.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(RepositoryIndexError) as raised:
            index.symbols(scope)
    finally:
        blocker.rollback()
        blocker.close()

    assert raised.value.code == "STORE_BUSY"
    assert raised.value.retryable is True


def test_branch_scope_is_explicit_and_results_do_not_leak(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    (repo / "payments.py").write_text("def feature_only():\n    return True\n")
    _commit(repo, "feature symbol")
    _git(repo, "checkout", "main")

    index = _index(tmp_path)
    index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))
    index.sync(SyncRequest(repo="billing", root=repo, branch="feature", revision="feature"))

    main = index.search(SearchRequest(IndexScope("billing", "main"), "feature_only"))
    feature = index.search(SearchRequest(IndexScope("billing", "feature"), "feature_only"))

    assert main.matches == ()
    assert feature.matches[0].component_id == "payments.py::feature_only"

    with pytest.raises(RepositoryIndexError) as raised:
        index.search(SearchRequest(IndexScope("billing", ""), "anything"))
    assert raised.value.code == "INVALID_REQUEST"


def test_repository_index_quality_gate_uses_real_git_corpus(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    (repo / "auth.py").write_text(
        "def validate_token(token):\n"
        "    \"\"\"Validate JWT access tokens.\"\"\"\n"
        "    return bool(token)\n"
    )
    (repo / "orders.py").write_text(
        "def create_order(items):\n"
        "    \"\"\"创建订单 校验库存\"\"\"\n"
        "    return list(items)\n"
    )
    (repo / "fees.py").write_text(
        "def calculate_fee(total):\n"
        "    \"\"\"Special rollover reconciliation fee.\"\"\"\n"
        "    return total * 0.01\n"
    )
    (repo / "routes.py").write_text(
        "from auth import validate_token\n\n"
        "def login(token):\n"
        "    \"\"\"Login endpoint for access tokens.\"\"\"\n"
        "    return validate_token(token)\n"
    )
    (repo / "noise.py").write_text(
        "def rotate_logs():\n"
        "    \"\"\"Archive old application logs.\"\"\"\n"
        "    return None\n"
    )
    _commit(repo, "quality corpus")

    index = _index(tmp_path)
    scope = IndexScope("quality", "main")
    index.sync(SyncRequest("quality", repo, "main", "main"))
    cases = [
        SearchCase("auth.py::validate_token", ("auth.py::validate_token",)),
        SearchCase("orders.py", ("orders.py::create_order",)),
        SearchCase("创建订单 校验库存", ("orders.py::create_order",)),
        SearchCase("special rollover reconciliation", ("fees.py::calculate_fee",)),
        SearchCase("login endpoint", ("routes.py::login",)),
    ]

    metrics = evaluate_search(
        lambda query, top_k: [
            {"id": hit.component_id}
            for hit in index.search(SearchRequest(scope, query, limit=top_k)).matches
        ],
        cases,
    )
    login = index.search(SearchRequest(scope, "login endpoint"))

    assert metrics == {"recall_at_5": 1.0, "mrr_at_10": 1.0, "ndcg_at_10": 1.0}
    assert login.matches[0].component_id == "routes.py::login"
    assert "auth.py::validate_token" in {hit.component_id for hit in login.related}


def test_enrichment_revision_is_atomic_and_enables_dense_recall(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    scope = IndexScope("billing", "main")
    sync = index.sync(SyncRequest("billing", repo, "main", "main"))

    before = index.search(SearchRequest(
        scope,
        "settle carried balance",
        retrieval="preferred",
    ))
    with pytest.raises(RepositoryIndexError) as required_before:
        index.search(SearchRequest(
            scope,
            "settle carried balance",
            retrieval="required",
        ))

    assert before.matches == ()
    assert before.retrieval == "local"
    assert before.degradations == ("dense_not_ready",)
    assert required_before.value.code == "HYBRID_REQUIRED_UNAVAILABLE"
    assert index.inspect(scope).dense_state == "pending"

    enrichment = index.enrich(scope)
    result = index.search(SearchRequest(
        scope,
        "settle carried balance",
        retrieval="preferred",
    ))
    status = index.inspect(scope)

    assert enrichment.generation == sync.generation
    assert enrichment.revision == 1
    assert enrichment.documents == 2
    assert enrichment.embedded_signatures == 2
    assert enrichment.dimension == 4
    assert result.retrieval == "hybrid"
    assert result.degradations == ()
    assert result.matches[0].component_id == "payments.py::create_order"
    assert result.matches[0].score_breakdown["dense"] > 0
    assert status.enrichment_revision == 1
    assert status.dense_state == "ready"
    assert status.pending_jobs == 0


def test_failed_enrichment_keeps_structural_generation_searchable(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    provider = FakeEmbeddingProvider()
    provider.fail_documents = True
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    scope = IndexScope("billing", "main")
    sync = index.sync(SyncRequest("billing", repo, "main", "main"))

    with pytest.raises(RepositoryIndexError) as raised:
        index.enrich(scope)

    status = index.inspect(scope)
    local = index.search(SearchRequest(scope, "create_order", retrieval="local"))
    preferred = index.search(SearchRequest(scope, "create_order", retrieval="preferred"))

    assert raised.value.code == "ENRICHMENT_FAILED"
    assert status.generation == sync.generation
    assert status.dense_state == "failed"
    assert status.enrichment_revision is None
    assert local.matches[0].component_id == "payments.py::create_order"
    assert preferred.matches[0].component_id == "payments.py::create_order"
    assert preferred.degradations == ("dense_not_ready",)


def test_incremental_enrichment_embeds_only_changed_content(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    first = index.enrich(scope)

    (repo / "payments.py").write_text(
        "def create_order(amount):\n"
        "    \"\"\"Create a revised payment order.\"\"\"\n"
        "    return amount + 1\n"
    )
    _commit(repo, "revise payment")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    pending = index.inspect(scope)
    second = index.enrich(scope)

    assert first.embedded_signatures == 2
    assert [len(batch) for batch in provider.document_batches] == [2, 1]
    assert pending.dense_state == "pending"
    assert pending.enrichment_revision is None
    assert second.revision == 2
    assert second.embedded_signatures == 1
    assert second.documents == 2


def test_cross_branch_enrichment_reuses_content_addressed_vectors(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    main = IndexScope("billing", "main")
    feature = IndexScope("billing", "feature")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    index.enrich(main)
    index.sync(SyncRequest("billing", repo, "feature", "feature"))
    reused = index.enrich(feature)

    assert [len(batch) for batch in provider.document_batches] == [2]
    assert reused.embedded_signatures == 0
    assert reused.reused_signatures == 2
    result = index.search(SearchRequest(
        feature,
        "settle carried balance",
        retrieval="required",
    ))
    assert result.matches[0].component_id == "payments.py::create_order"
    with sqlite3.connect(tmp_path / "repository-index.sqlite3") as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM embedding_buckets"
        ).fetchone()[0] == 2 * 8


def test_concurrent_cross_branch_enrichment_buckets_match_stored_vectors(
    tmp_path: Path,
):
    class SequencedProvider(FakeEmbeddingProvider):
        model = "concurrent-semantic-v1"

        def __init__(self):
            super().__init__()
            self._lock = threading.Lock()
            self._calls = 0
            self.first_entered = threading.Event()
            self.second_entered = threading.Event()
            self.first_done = threading.Event()

        def embed_documents(self, texts):
            batch = list(texts)
            with self._lock:
                call = self._calls
                self._calls += 1
            if call == 0:
                self.first_entered.set()
                assert self.second_entered.wait(5)
                vector = [1.0, -1.0, 1.0, -1.0]
            else:
                self.second_entered.set()
                assert self.first_done.wait(5)
                vector = [-1.0, 1.0, -1.0, 1.0]
            self.document_batches.append(batch)
            return [vector for _ in batch]

    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "branch", "feature")
    database = tmp_path / "repository-index.sqlite3"
    provider = SequencedProvider()
    index = RepositoryIndex(database, embedding_provider=provider)
    main = IndexScope("billing", "main")
    feature = IndexScope("billing", "feature")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    index.sync(SyncRequest("billing", repo, "feature", "feature"))

    def enrich_main():
        try:
            return RepositoryIndex(database, embedding_provider=provider).enrich(main)
        finally:
            provider.first_done.set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(enrich_main)
        assert provider.first_entered.wait(5)
        second = executor.submit(
            RepositoryIndex(database, embedding_provider=provider).enrich,
            feature,
        )
        reports = (first.result(), second.result())

    assert {report.scope.branch for report in reports} == {"main", "feature"}
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        embeddings = list(connection.execute(
            """
            SELECT content_signature, dimension, vector
            FROM embeddings
            WHERE model = ?
            """,
            (provider.model,),
        ))
        for embedding in embeddings:
            vector = repository_index_module._unpack_vector(
                embedding["vector"],
                int(embedding["dimension"]),
            )
            expected = tuple(enumerate(
                repository_index_module._lsh_buckets(vector, provider.model)
            ))
            actual = tuple(
                tuple(row)
                for row in connection.execute(
                    """
                    SELECT table_no, bucket
                    FROM embedding_buckets
                    WHERE content_signature = ? AND model = ?
                    ORDER BY table_no
                    """,
                    (embedding["content_signature"], provider.model),
                )
            )
            assert actual == expected


def test_concurrent_enrichment_of_same_generation_has_single_owner(tmp_path: Path):
    class BlockingProvider(FakeEmbeddingProvider):
        def __init__(self):
            super().__init__()
            self._lock = threading.Lock()
            self._calls = 0
            self.first_entered = threading.Event()
            self.release_first = threading.Event()

        def embed_documents(self, texts):
            with self._lock:
                call = self._calls
                self._calls += 1
            if call == 0:
                self.first_entered.set()
                assert self.release_first.wait(5)
            return super().embed_documents(texts)

    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    provider = BlockingProvider()
    index = RepositoryIndex(database, embedding_provider=provider)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    competing_error = None
    first_error = None

    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(
            RepositoryIndex(database, embedding_provider=provider).enrich,
            scope,
        )
        assert provider.first_entered.wait(5)
        maintenance = index.maintain()
        try:
            RepositoryIndex(database, embedding_provider=provider).enrich(scope)
        except RepositoryIndexError as error:
            competing_error = error
        finally:
            provider.release_first.set()
        try:
            first_report = first.result()
        except RepositoryIndexError as error:
            first_error = error
            first_report = None

    assert first_error is None
    assert first_report is not None
    assert competing_error is not None
    assert competing_error.code == "ENRICHMENT_BUSY"
    assert competing_error.retryable is True
    assert maintenance.recovered_jobs == 0
    assert len(provider.document_batches) == 1
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT attempts FROM enrichment_jobs"
        ).fetchone()[0] == 1


def test_recovered_enrichment_rejects_stale_owner_publication(
    monkeypatch,
    tmp_path: Path,
):
    class ReclaimableProvider(FakeEmbeddingProvider):
        def __init__(self):
            super().__init__()
            self._lock = threading.Lock()
            self._calls = 0
            self.first_entered = threading.Event()
            self.release_first = threading.Event()

        def embed_documents(self, texts):
            with self._lock:
                call = self._calls
                self._calls += 1
            if call == 0:
                self.first_entered.set()
                assert self.release_first.wait(5)
            return super().embed_documents(texts)

    monkeypatch.setattr("indexer.repository_index.ENRICHMENT_LEASE_SECONDS", 0)
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    provider = ReclaimableProvider()
    index = RepositoryIndex(database, embedding_provider=provider)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(
            RepositoryIndex(database, embedding_provider=provider).enrich,
            scope,
        )
        assert provider.first_entered.wait(5)
        maintenance = RepositoryIndex(database).maintain()
        replacement = RepositoryIndex(
            database,
            embedding_provider=provider,
        ).enrich(scope)
        provider.release_first.set()
        with pytest.raises(RepositoryIndexError) as stale:
            first.result()

    assert maintenance.recovered_jobs == 1
    assert replacement.revision == 1
    assert stale.value.code == "ENRICHMENT_STALE"
    assert stale.value.retryable is True
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM enrichment_revisions"
        ).fetchone()[0] == 1


def test_reconcile_branches_removes_inactive_scope_and_orphans(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    _git(repo, "checkout", "-b", "feature")
    (repo / "payments.py").write_text("def feature_order():\n    return True\n")
    _commit(repo, "feature payment")
    _git(repo, "checkout", "main")

    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    main = IndexScope("billing", "main")
    feature = IndexScope("billing", "feature")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    index.sync(SyncRequest("billing", repo, "feature", "feature"))

    report = index.reconcile_branches("billing", ("feature",))

    assert report.removed_branches == ("main",)
    assert report.deleted_snapshots >= 1
    assert index.inspect(main).exists is False
    assert index.inspect(feature).exists is True
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM branch_heads WHERE repo_id = 'billing'"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM parse_artifacts"
        ).fetchone()[0] == 2
        assert connection.execute(
            "SELECT COUNT(*) FROM artifact_documents"
        ).fetchone()[0] == 2


def test_enrichment_is_idempotent_for_published_model_and_generation(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    first = index.enrich(scope)
    second = index.enrich(scope)

    assert first.revision == second.revision == 1
    assert second.embedded_signatures == 0
    assert [len(batch) for batch in provider.document_batches] == [2]


def test_dense_query_failure_degrades_preferred_and_fails_required(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(
        tmp_path / "repository-index.sqlite3",
        embedding_provider=provider,
    )
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))
    index.enrich(scope)
    provider.fail_query = True

    preferred = index.search(SearchRequest(scope, "create_order", retrieval="preferred"))
    with pytest.raises(RepositoryIndexError) as required:
        index.search(SearchRequest(scope, "create_order", retrieval="required"))

    assert preferred.retrieval == "local"
    assert preferred.matches[0].component_id == "payments.py::create_order"
    assert preferred.degradations == ("dense_query_failed:RuntimeError",)
    assert required.value.code == "HYBRID_REQUIRED_UNAVAILABLE"


def test_sync_retains_two_generations_without_sweeping_live_overlay_chain(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    scope = IndexScope("billing", "main")

    index.sync(SyncRequest("billing", repo, "main", "main"))
    for revision in range(2, 5):
        (repo / "payments.py").write_text(
            "def create_order(amount):\n"
            f"    return amount + {revision}\n"
        )
        _commit(repo, f"revision {revision}")
        index.sync(SyncRequest("billing", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        generations = connection.execute(
            "SELECT generation FROM generations ORDER BY generation"
        ).fetchall()
        artifacts = int(connection.execute(
            "SELECT COUNT(*) FROM parse_artifacts"
        ).fetchone()[0])
        snapshots = int(connection.execute(
            "SELECT COUNT(*) FROM snapshots"
        ).fetchone()[0])

    assert generations == [(3,), (4,)]
    assert snapshots == 4
    assert artifacts == index.inspect(scope).files + 3
    assert index.integrity().ok is True


def test_depth_checkpoint_prefers_full_snapshot_over_larger_divergent_overlay(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr("indexer.repository_index.MAX_SNAPSHOT_DEPTH", 2)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "repo-wiki@example.test")
    _git(repo, "config", "user.name", "repo-wiki test")
    for number in range(12):
        (repo / f"main_{number}.py").write_text(
            f"def main_{number}():\n    return {number}\n"
        )
    initial_commit = _commit(repo, "main corpus")
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("checkpoint", repo, "main", "main"))
    (repo / "main_0.py").write_text("def main_0():\n    return 100\n")
    _commit(repo, "main overlay")
    index.sync(SyncRequest("checkpoint", repo, "main", "main"))

    _git(repo, "checkout", "-b", "feature", initial_commit)
    for path in repo.glob("main_*.py"):
        path.unlink()
    for number in range(12):
        (repo / f"feature_{number}.py").write_text(
            f"def feature_{number}():\n    return {number}\n"
        )
    _commit(repo, "divergent feature corpus")
    index.sync(SyncRequest("checkpoint", repo, "feature", "feature"))

    _git(repo, "checkout", "main")
    (repo / "main_1.py").write_text("def main_1():\n    return 101\n")
    _commit(repo, "checkpoint main")
    index.sync(SyncRequest("checkpoint", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        snapshot = connection.execute(
            """
            SELECT s.id, s.base_snapshot_id
            FROM branch_heads AS h
            JOIN generations AS g ON g.id = h.generation_id
            JOIN snapshots AS s ON s.id = g.snapshot_id
            WHERE h.repo_id = 'checkpoint' AND h.branch = 'main'
            """
        ).fetchone()
        changes = connection.execute(
            "SELECT COUNT(*) FROM snapshot_changes WHERE snapshot_id = ?",
            (snapshot[0],),
        ).fetchone()[0]

    assert snapshot[1] is None
    assert changes == 12


def test_maintenance_recovers_interrupted_current_enrichment(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    provider = FakeEmbeddingProvider()
    index = RepositoryIndex(database, embedding_provider=provider)
    scope = IndexScope("billing", "main")
    index.sync(SyncRequest("billing", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            UPDATE enrichment_jobs
            SET status = 'running', updated_at = '2000-01-01T00:00:00+00:00'
            WHERE status = 'pending'
            """
        )
        connection.commit()

    report = index.maintain()
    status = index.inspect(scope)
    enrichment = index.enrich(scope)

    assert report.recovered_jobs == 1
    assert report.integrity.ok is True
    assert status.dense_state == "pending"
    assert enrichment.revision == 1


def test_integrity_reports_foreign_key_violations(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    database = tmp_path / "repository-index.sqlite3"
    index = RepositoryIndex(database)
    index.sync(SyncRequest("billing", repo, "main", "main"))

    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("UPDATE branch_heads SET generation_id = 999999")
        connection.commit()

    report = index.integrity()

    assert report.ok is False
    assert report.message == "ok"
    assert report.foreign_key_violations == 1
