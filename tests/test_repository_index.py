from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

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


def test_wiki_projection_is_rendered_from_published_generation(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    scope = IndexScope("billing", "main")
    sync = index.sync(SyncRequest("billing", repo, "main", "main"))
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


def test_same_blob_is_parsed_once_across_branches(monkeypatch, tmp_path: Path):
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
        files = int(connection.execute("SELECT COUNT(*) FROM files").fetchone()[0])
        artifacts = int(connection.execute(
            "SELECT COUNT(*) FROM parse_artifacts"
        ).fetchone()[0])
    assert files == 4
    assert artifacts == 2


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


def test_transaction_failure_rolls_back_materialized_state(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    _write_repository(repo)
    index = _index(tmp_path)
    first = index.sync(SyncRequest(repo="billing", root=repo, branch="main", revision="main"))

    (repo / "payments.py").write_text("def replacement():\n    return True\n")
    _commit(repo, "replacement")

    def fail_relations(*args, **kwargs):
        raise RuntimeError("relation invariant failed")

    monkeypatch.setattr(index, "_rebuild_relations", fail_relations)
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
    lexical = index.search(SearchRequest(IndexScope("billing", "main"), "payment order"))

    assert exact.generation == report.generation
    assert exact.tree_id == report.tree_id
    assert exact.retrieval == "local"
    assert exact.degradations == ()
    assert exact.matches[0].component_id == "payments.py::create_order"
    assert exact.matches[0].score_breakdown["exact"] > 0
    assert [hit.component_id for hit in exact.related] == ["service.py::checkout"]
    assert lexical.matches[0].component_id == "payments.py::create_order"
    assert lexical.matches[0].score_breakdown["lexical"] > 0


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


def test_sync_collects_old_generations_and_orphan_artifacts(tmp_path: Path):
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

    assert generations == [(3,), (4,)]
    assert artifacts == index.inspect(scope).files
    assert index.integrity().ok is True


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
            "UPDATE enrichment_jobs SET status = 'running' WHERE status = 'pending'"
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
