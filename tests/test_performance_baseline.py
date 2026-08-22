from __future__ import annotations

from indexer.repository_benchmarks import run_repository_index_benchmark


def test_repository_index_generation_cost_scales_with_delta():
    rows = run_repository_index_benchmark((5, 20), query_runs=5)

    assert [row["files"] for row in rows] == [5, 20]
    for row in rows:
        assert row["full"]["parsed_blobs"] == row["files"]
        assert row["incremental"]["changed_files"] == 1
        assert row["incremental"]["parsed_blobs"] == 1
        assert row["incremental"]["tree_entries_scanned"] == 1
        assert row["unchanged"]["status"] == "unchanged"
        assert row["unchanged"]["parsed_blobs"] == 0
        assert row["unchanged"]["tree_entries_scanned"] == 0
        assert row["latest_generation_changes"] == 1
        assert row["generations"] == 2
        assert row["parse_artifacts"] == row["files"] + 1
        assert row["feature_overlay"]["parsed_blobs"] == 1
        assert row["feature_overlay"]["reused_blobs"] == row["files"] - 1
        assert row["feature_overlay"]["snapshot_changes"] == 1
        assert row["feature_overlay"]["artifact_documents"] == row["files"] + 2
        assert row["feature_overlay"]["fts_documents"] == row["files"] + 2
        assert row["query_p95_ms"] < 500
        assert row["database_bytes"] > 0
