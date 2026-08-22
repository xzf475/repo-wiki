from __future__ import annotations

import json
import math
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from indexer.repository_index import IndexScope, RepositoryIndex, SearchRequest, SyncRequest


def run_repository_index_benchmark(
    sizes: tuple[int, ...] = (10, 100, 500),
    *,
    query_runs: int = 20,
) -> list[dict]:
    if query_runs < 1:
        raise ValueError("query_runs must be positive")
    rows = []
    for size in sizes:
        if size < 1:
            raise ValueError("benchmark sizes must be positive")
        with tempfile.TemporaryDirectory(prefix="repo-wiki-generation-benchmark-") as directory:
            root = Path(directory)
            repo = root / "repo"
            database = root / "repository-index.sqlite3"
            repo.mkdir()
            _git(repo, "init", "-b", "main")
            _git(repo, "config", "user.email", "benchmark@example.test")
            _git(repo, "config", "user.name", "repo-wiki benchmark")
            for index in range(size):
                (repo / f"module_{index:05d}.py").write_text(
                    f"def handler_{index}():\n"
                    f"    \"\"\"Handle customer record partition {index}.\"\"\"\n"
                    f"    return {index}\n",
                    encoding="utf-8",
                )
            _commit(repo, "initial")

            repository_index = RepositoryIndex(database)
            request = SyncRequest("benchmark", repo, "main", "main")
            full = repository_index.sync(request)

            (repo / "module_00000.py").write_text(
                "def handler_0():\n"
                "    \"\"\"Handle updated customer record partition.\"\"\"\n"
                "    return 1000000\n",
                encoding="utf-8",
            )
            _commit(repo, "update one file")
            incremental = repository_index.sync(request)
            unchanged = repository_index.sync(request)

            query_times = []
            for _ in range(query_runs):
                result = repository_index.search(SearchRequest(
                    IndexScope("benchmark", "main"),
                    "customer record partition",
                    limit=10,
                    related_limit=0,
                ))
                query_times.append(result.elapsed_ms)

            with sqlite3.connect(database) as connection:
                parse_artifacts = int(connection.execute(
                    "SELECT COUNT(*) FROM parse_artifacts"
                ).fetchone()[0])
                generations = int(connection.execute(
                    "SELECT COUNT(*) FROM generations"
                ).fetchone()[0])
                latest_changes = int(connection.execute(
                    """
                    SELECT COUNT(*) FROM generation_changes
                    WHERE generation_id = (SELECT MAX(id) FROM generations)
                    """
                ).fetchone()[0])

            _git(repo, "checkout", "-b", "feature")
            (repo / "module_00000.py").write_text(
                "def feature_handler():\n"
                "    \"\"\"Handle a feature-only customer record.\"\"\"\n"
                "    return 2000000\n",
                encoding="utf-8",
            )
            _commit(repo, "feature update")
            feature = repository_index.sync(SyncRequest(
                "benchmark", repo, "feature", "feature"
            ))
            with sqlite3.connect(database) as connection:
                feature_snapshot_id = int(connection.execute(
                    """
                    SELECT g.snapshot_id
                    FROM branch_heads AS h
                    JOIN generations AS g ON g.id = h.generation_id
                    WHERE h.repo_id = 'benchmark' AND h.branch = 'feature'
                    """
                ).fetchone()[0])
                feature_overlay_rows = int(connection.execute(
                    "SELECT COUNT(*) FROM snapshot_changes WHERE snapshot_id = ?",
                    (feature_snapshot_id,),
                ).fetchone()[0])
                artifact_documents = int(connection.execute(
                    "SELECT COUNT(*) FROM artifact_documents"
                ).fetchone()[0])
                fts_documents = int(connection.execute(
                    "SELECT COUNT(*) FROM artifact_documents_fts"
                ).fetchone()[0])

            rows.append({
                "files": size,
                "full": _sync_metrics(full),
                "incremental": _sync_metrics(incremental),
                "unchanged": _sync_metrics(unchanged),
                "query_p95_ms": _percentile(query_times, 0.95),
                "query_max_ms": round(max(query_times), 3),
                "database_bytes": _database_bytes(database),
                "parse_artifacts": parse_artifacts,
                "generations": generations,
                "latest_generation_changes": latest_changes,
                "feature_overlay": {
                    **_sync_metrics(feature),
                    "snapshot_changes": feature_overlay_rows,
                    "artifact_documents": artifact_documents,
                    "fts_documents": fts_documents,
                },
            })
    return rows


def _sync_metrics(report) -> dict[str, int | float | str]:
    return {
        "status": report.status,
        "elapsed_ms": report.elapsed_ms,
        "changed_files": len(report.changed_files),
        "removed_files": len(report.removed_files),
        "parsed_blobs": report.parsed_blobs,
        "reused_blobs": report.reused_blobs,
        "tree_entries_scanned": report.tree_entries_scanned,
    }


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * percentile) - 1))
    return round(ordered[index], 3)


def _database_bytes(database: Path) -> int:
    return sum(
        path.stat().st_size
        for path in (
            database,
            database.with_name(f"{database.name}-wal"),
            database.with_name(f"{database.name}-shm"),
        )
        if path.exists()
    )


def main() -> None:
    print(json.dumps(run_repository_index_benchmark(), indent=2))


__all__ = ["run_repository_index_benchmark"]


if __name__ == "__main__":
    main()
