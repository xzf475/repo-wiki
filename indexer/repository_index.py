from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import tempfile
import time
from array import array
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Protocol, Sequence, TypeVar
from uuid import uuid4

from indexer.ast_parser import ASTNode, parse_file
from indexer.git_snapshot import GitSnapshot, GitSnapshotError, TreeDelta, TreeEntry
from indexer.repository_store import (
    RepositoryStore,
    RepositoryStoreError,
    RepositoryStoreVersionError,
)


PARSER_VERSION = "semantic-ast-v1"
RRF_K = 60
MAX_LIMIT = 100
LSH_TABLES = 8
LSH_BITS = 10
DENSE_CANDIDATE_MULTIPLIER = 8
MAX_SNAPSHOT_DEPTH = 32
ENRICHMENT_LEASE_SECONDS = 15 * 60
RETRIEVAL_MODES = frozenset({"local", "preferred", "required"})
_T = TypeVar("_T")

_RESOLVED_FILES_CTE = """
WITH RECURSIVE snapshot_chain(snapshot_id, depth) AS (
    SELECT ?, 0
    UNION ALL
    SELECT s.base_snapshot_id, c.depth + 1
    FROM snapshots AS s
    JOIN snapshot_chain AS c ON s.id = c.snapshot_id
    WHERE s.base_snapshot_id IS NOT NULL
),
ranked_files AS (
    SELECT
        sc.path,
        sc.path_key,
        sc.blob_id,
        sc.artifact_id,
        sc.kind,
        ROW_NUMBER() OVER (
            PARTITION BY sc.path
            ORDER BY c.depth
        ) AS position
    FROM snapshot_chain AS c
    JOIN snapshot_changes AS sc ON sc.snapshot_id = c.snapshot_id
),
resolved_files AS (
    SELECT path, path_key, blob_id, artifact_id
    FROM ranked_files
    WHERE position = 1 AND kind = 'upsert'
)
"""


class EmbeddingProvider(Protocol):
    model: str

    def embed_documents(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...

    def embed_query(self, text: str) -> Sequence[float]: ...


class RepositoryIndexError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        phase: str,
        target: str = "",
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.phase = phase
        self.target = target
        self.retryable = retryable


@dataclass(frozen=True)
class IndexScope:
    repo: str
    branch: str


@dataclass(frozen=True)
class SyncRequest:
    repo: str
    root: Path
    branch: str
    revision: str = "HEAD"


@dataclass(frozen=True)
class SyncReport:
    status: str
    repo: str
    branch: str
    generation: int
    tree_id: str
    changed_files: tuple[str, ...]
    removed_files: tuple[str, ...]
    parsed_blobs: int
    reused_blobs: int
    tree_entries_scanned: int
    elapsed_ms: float


@dataclass(frozen=True)
class SearchRequest:
    scope: IndexScope
    query: str
    limit: int = 10
    related_limit: int | None = None
    retrieval: str = "local"


@dataclass(frozen=True)
class SearchHit:
    component_id: str
    file: str
    symbol: str
    type: str
    line_start: int
    line_end: int
    source: str
    score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class SymbolRecord:
    component_id: str
    file: str
    symbol: str
    type: str
    line_start: int
    line_end: int
    docstring: str
    source: str
    imports: tuple[str, ...] = ()
    calls: tuple[str, ...] = ()
    called_by: tuple[str, ...] = ()
    entry_point_kind: str = ""
    entry_point_path: str = ""


@dataclass(frozen=True)
class SearchResult:
    scope: IndexScope
    generation: int
    tree_id: str
    matches: tuple[SearchHit, ...]
    related: tuple[SearchHit, ...]
    retrieval: str
    degradations: tuple[str, ...]
    elapsed_ms: float


@dataclass(frozen=True)
class IndexStatus:
    scope: IndexScope
    exists: bool
    generation: int | None
    tree_id: str
    files: int
    symbols: int
    relations: int
    enrichment_revision: int | None = None
    dense_state: str = "not_ready"
    pending_jobs: int = 0


@dataclass(frozen=True)
class EnrichmentReport:
    scope: IndexScope
    generation: int
    revision: int
    model: str
    dimension: int
    documents: int
    embedded_signatures: int
    reused_signatures: int
    elapsed_ms: float


@dataclass(frozen=True)
class IntegrityReport:
    ok: bool
    message: str
    foreign_key_violations: int


@dataclass(frozen=True)
class MaintenanceReport:
    retained_generations: int
    recovered_jobs: int
    superseded_jobs: int
    deleted_generations: int
    deleted_revisions: int
    deleted_artifacts: int
    deleted_embeddings: int
    deleted_buckets: int
    deleted_snapshots: int
    deleted_snapshot_objects: int
    reclaimed_pages: int
    integrity: IntegrityReport


@dataclass(frozen=True)
class BranchReconcileReport:
    repo: str
    active_branches: tuple[str, ...]
    removed_branches: tuple[str, ...]
    deleted_snapshots: int
    deleted_artifacts: int
    deleted_embeddings: int
    reclaimed_pages: int


@dataclass(frozen=True)
class _Head:
    generation_id: int
    generation: int
    tree_id: str
    snapshot_id: int


@dataclass(frozen=True)
class _SnapshotRef:
    snapshot_id: int
    tree_id: str
    depth: int


@dataclass(frozen=True)
class _PreparedArtifacts:
    entry_artifacts: dict[str, str]
    payloads: dict[str, str]
    new_payloads: dict[str, tuple[str, str, str, str]]
    parsed_blobs: int
    reused_blobs: int


@dataclass(frozen=True)
class _DenseState:
    generation_id: int
    revision_id: int
    revision: int
    model: str
    dimension: int


@dataclass(frozen=True)
class _MaintenanceCounts:
    recovered_jobs: int
    superseded_jobs: int
    deleted_generations: int
    deleted_revisions: int
    deleted_artifacts: int
    deleted_embeddings: int
    deleted_buckets: int
    deleted_snapshots: int


class RepositoryIndex:
    """Transactional, content-addressed repository index.

    Git capture, parsing, graph maintenance, FTS, enrichment, maintenance, and
    transaction boundaries remain private implementation details behind a small
    repository-oriented interface.
    """

    def __init__(
        self,
        database: Path,
        *,
        embedding_provider: EmbeddingProvider | None = None,
    ):
        self._embedding_provider = embedding_provider
        try:
            self._store = RepositoryStore(database)
        except RepositoryStoreVersionError as error:
            raise RepositoryIndexError(
                "STORE_INCOMPATIBLE",
                str(error),
                phase="initialize",
            ) from error
        except RepositoryStoreError as error:
            raise RepositoryIndexError(
                "STORE_CORRUPT",
                str(error),
                phase="initialize",
            ) from error

    @classmethod
    def open(
        cls,
        root: Path,
        *,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> "RepositoryIndex":
        return cls(
            root / ".indexer" / "state" / "repository-index.sqlite3",
            embedding_provider=embedding_provider,
        )

    def sync(self, request: SyncRequest) -> SyncReport:
        started = time.perf_counter()
        scope = IndexScope(request.repo, request.branch)
        self._validate_scope(scope)
        if not request.revision.strip():
            self._raise_invalid("revision must not be empty", scope)

        with GitSnapshot(request.root) as snapshot:
            try:
                tree_id = snapshot.resolve_tree(request.revision)
            except GitSnapshotError as error:
                raise RepositoryIndexError(
                    "SOURCE_UNAVAILABLE",
                    str(error),
                    phase="capture",
                    target=_target(scope),
                    retryable=True,
                ) from error

            head = self._read_head(scope)
            if head and head.tree_id == tree_id:
                return SyncReport(
                    status="unchanged",
                    repo=scope.repo,
                    branch=scope.branch,
                    generation=head.generation,
                    tree_id=tree_id,
                    changed_files=(),
                    removed_files=(),
                    parsed_blobs=0,
                    reused_blobs=0,
                    tree_entries_scanned=0,
                    elapsed_ms=_elapsed_ms(started),
                )

            try:
                logical_delta = (
                    snapshot.delta(head.tree_id, tree_id)
                    if head
                    else snapshot.initial_delta(tree_id)
                )
                existing_snapshot = self._read_snapshot(scope.repo, tree_id)
                if existing_snapshot is not None:
                    snapshot_base = None
                    snapshot_delta = TreeDelta((), (), 0)
                else:
                    snapshot_base, snapshot_delta = self._select_snapshot_base(
                        snapshot,
                        scope.repo,
                        tree_id,
                        head,
                        logical_delta,
                    )
                    if (
                        snapshot_base is not None
                        and not snapshot_delta.changed
                        and not snapshot_delta.removed
                    ):
                        existing_snapshot = snapshot_base
                        snapshot_base = None
                prepared = self._prepare_artifacts(snapshot, snapshot_delta.changed)
                parsed_blobs = prepared.parsed_blobs
                reused_blobs = max(
                    prepared.reused_blobs,
                    len(logical_delta.changed) - parsed_blobs,
                )
            except GitSnapshotError as error:
                raise RepositoryIndexError(
                    "SOURCE_UNAVAILABLE",
                    str(error),
                    phase="capture",
                    target=_target(scope),
                    retryable=True,
                ) from error
            except RepositoryIndexError:
                raise
            except Exception as error:
                raise RepositoryIndexError(
                    "PARSE_FAILED",
                    str(error),
                    phase="parse",
                    target=_target(scope),
                ) from error
            snapshot_leases = snapshot.detach_snapshot_leases()

        try:
            generation = self._publish_generation(
                scope=scope,
                source_root=request.root.resolve(),
                tree_id=tree_id,
                expected_head=head,
                delta=logical_delta,
                snapshot_delta=snapshot_delta,
                snapshot_base=snapshot_base,
                existing_snapshot=existing_snapshot,
                prepared=prepared,
                parsed_blobs=parsed_blobs,
                reused_blobs=reused_blobs,
            )
        except RepositoryIndexError:
            raise
        except sqlite3.OperationalError as error:
            raise RepositoryIndexError(
                "STORE_BUSY" if "locked" in str(error).casefold() else "STORE_CORRUPT",
                str(error),
                phase="commit",
                target=_target(scope),
                retryable="locked" in str(error).casefold(),
            ) from error
        except sqlite3.Error as error:
            raise RepositoryIndexError(
                "STORE_CORRUPT",
                str(error),
                phase="commit",
                target=_target(scope),
            ) from error
        except Exception as error:
            raise RepositoryIndexError(
                "INVARIANT_VIOLATION",
                str(error),
                phase="commit",
                target=_target(scope),
            ) from error
        finally:
            GitSnapshot.release_snapshot_leases(snapshot_leases)

        return SyncReport(
            status="published",
            repo=scope.repo,
            branch=scope.branch,
            generation=generation,
            tree_id=tree_id,
            changed_files=tuple(entry.path for entry in logical_delta.changed),
            removed_files=logical_delta.removed,
            parsed_blobs=parsed_blobs,
            reused_blobs=reused_blobs,
            tree_entries_scanned=logical_delta.entries_scanned,
            elapsed_ms=_elapsed_ms(started),
        )

    def enrich(self, scope: IndexScope) -> EnrichmentReport:
        """Complete the pending dense revision for the current generation."""
        started = time.perf_counter()
        self._validate_scope(scope)
        provider = self._embedding_provider
        if provider is None:
            raise RepositoryIndexError(
                "ENRICHMENT_UNAVAILABLE",
                "embedding provider is not configured",
                phase="enrich",
                target=_target(scope),
                retryable=True,
            )
        model = _provider_model(provider)
        owner_token = uuid4().hex

        with self._store.transaction(write=True) as connection:
            head = self._head(connection, scope)
            if not head:
                raise RepositoryIndexError(
                    "INDEX_NOT_FOUND",
                    f"index not found for {_target(scope)}",
                    phase="enrich",
                    target=_target(scope),
                )
            existing_revision = self._dense_state(connection, scope, head.generation_id)
            if existing_revision and existing_revision.model == model:
                documents = self._document_count(connection, head.snapshot_id)
                return EnrichmentReport(
                    scope=scope,
                    generation=head.generation,
                    revision=existing_revision.revision,
                    model=model,
                    dimension=existing_revision.dimension,
                    documents=documents,
                    embedded_signatures=0,
                    reused_signatures=0,
                    elapsed_ms=_elapsed_ms(started),
                )
            timestamp = _timestamp()
            claimable_statuses = ("pending", "failed")
            if existing_revision is not None:
                claimable_statuses += ("completed",)
            placeholders = ",".join("?" for _ in claimable_statuses)
            claim = connection.execute(
                f"""
                UPDATE enrichment_jobs
                SET status = 'running', attempts = attempts + 1,
                    error = '', owner_token = ?, updated_at = ?
                WHERE generation_id = ?
                  AND status IN ({placeholders})
                """,
                (
                    owner_token,
                    timestamp,
                    head.generation_id,
                    *claimable_statuses,
                ),
            )
            if not claim.rowcount:
                concurrent_revision = self._dense_state(
                    connection,
                    scope,
                    head.generation_id,
                )
                if concurrent_revision and concurrent_revision.model == model:
                    documents = self._document_count(connection, head.snapshot_id)
                    return EnrichmentReport(
                        scope=scope,
                        generation=head.generation,
                        revision=concurrent_revision.revision,
                        model=model,
                        dimension=concurrent_revision.dimension,
                        documents=documents,
                        embedded_signatures=0,
                        reused_signatures=0,
                        elapsed_ms=_elapsed_ms(started),
                    )
                job = connection.execute(
                    "SELECT status FROM enrichment_jobs WHERE generation_id = ?",
                    (head.generation_id,),
                ).fetchone()
                if job and job["status"] == "running":
                    raise RepositoryIndexError(
                        "ENRICHMENT_BUSY",
                        f"enrichment already running for {_target(scope)}",
                        phase="enrich",
                        target=_target(scope),
                        retryable=True,
                    )
                raise RepositoryIndexError(
                    "ENRICHMENT_STATE_INVALID",
                    f"current enrichment job is not claimable for {_target(scope)}",
                    phase="enrich",
                    target=_target(scope),
                )

        try:
            with self._store.transaction() as connection:
                current = self._head(connection, scope)
                if _head_identity(current) != _head_identity(head):
                    raise RepositoryIndexError(
                        "ENRICHMENT_STALE",
                        "structural generation changed before enrichment started",
                        phase="enrich",
                        target=_target(scope),
                        retryable=True,
                    )
                rows = list(connection.execute(
                    _RESOLVED_FILES_CTE + """
                    SELECT
                        rf.path || '::' || d.local_id AS component_id,
                        d.text,
                        d.content_signature,
                        e.content_signature AS mapped_signature,
                        e.model AS mapped_model
                    FROM resolved_files AS rf
                    JOIN artifact_documents AS d
                      ON d.artifact_id = rf.artifact_id
                    LEFT JOIN embeddings AS e
                      ON e.content_signature = d.content_signature
                     AND e.model = ?
                    ORDER BY component_id
                    """,
                    (head.snapshot_id, model),
                ))

            missing_documents = [
                row for row in rows
                if row["mapped_signature"] != row["content_signature"]
                or row["mapped_model"] != model
            ]
            texts_by_signature: dict[str, str] = {}
            for row in missing_documents:
                texts_by_signature.setdefault(row["content_signature"], row["text"])

            cached_vectors = self._load_embedding_vectors(
                tuple(texts_by_signature),
                model,
            )
            uncached_signatures = [
                signature
                for signature in texts_by_signature
                if signature not in cached_vectors
            ]
            new_vectors: dict[str, tuple[float, ...]] = {}
            if uncached_signatures:
                embedded = provider.embed_documents([
                    texts_by_signature[signature]
                    for signature in uncached_signatures
                ])
                if len(embedded) != len(uncached_signatures):
                    raise ValueError(
                        "embedding provider returned a different number of vectors than inputs"
                    )
                for signature, vector in zip(uncached_signatures, embedded, strict=True):
                    new_vectors[signature] = _normalize_vector(vector)

            vectors = dict(cached_vectors)
            vectors.update(new_vectors)
            dimensions = {len(vector) for vector in vectors.values()}
            if len(dimensions) > 1:
                raise ValueError("embedding provider returned inconsistent dimensions")

            with self._store.transaction(write=True) as connection:
                actual_head = self._head(connection, scope)
                if _head_identity(actual_head) != _head_identity(head):
                    raise RepositoryIndexError(
                        "ENRICHMENT_STALE",
                        "structural generation changed during enrichment",
                        phase="enrich",
                        target=_target(scope),
                        retryable=True,
                    )
                job_owner = connection.execute(
                    """
                    SELECT status, owner_token
                    FROM enrichment_jobs
                    WHERE generation_id = ?
                    """,
                    (head.generation_id,),
                ).fetchone()
                if (
                    not job_owner
                    or job_owner["status"] != "running"
                    or job_owner["owner_token"] != owner_token
                ):
                    raise RepositoryIndexError(
                        "ENRICHMENT_STALE",
                        "enrichment ownership changed during provider execution",
                        phase="enrich",
                        target=_target(scope),
                        retryable=True,
                    )
                timestamp = _timestamp()
                for signature, vector in new_vectors.items():
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO embeddings(
                            content_signature, model, dimension, vector, created_at
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (signature, model, len(vector), _pack_vector(vector), timestamp),
                    )

                authoritative_vectors: dict[str, tuple[float, ...]] = {}
                signatures = tuple(texts_by_signature)
                for chunk in _chunks(signatures):
                    placeholders = ",".join("?" for _ in chunk)
                    stored_rows = connection.execute(
                        f"""
                        SELECT content_signature, dimension, vector
                        FROM embeddings
                        WHERE model = ?
                          AND content_signature IN ({placeholders})
                        """,
                        (model, *chunk),
                    )
                    for stored_row in stored_rows:
                        authoritative_vectors[stored_row["content_signature"]] = (
                            _unpack_vector(
                                stored_row["vector"],
                                int(stored_row["dimension"]),
                            )
                        )
                if len(authoritative_vectors) != len(signatures):
                    raise RuntimeError("enrichment vectors disappeared before publication")
                authoritative_dimensions = {
                    len(vector) for vector in authoritative_vectors.values()
                }
                if len(authoritative_dimensions) > 1:
                    raise RuntimeError("stored embeddings have inconsistent dimensions")

                for signature, vector in authoritative_vectors.items():
                    connection.executemany(
                        """
                        INSERT INTO embedding_buckets(
                            content_signature, model, table_no, bucket
                        ) VALUES (?, ?, ?, ?)
                        ON CONFLICT(content_signature, model, table_no)
                        DO UPDATE SET bucket = excluded.bucket
                        """,
                        [
                            (
                                signature,
                                model,
                                table_no,
                                bucket,
                            )
                            for table_no, bucket in enumerate(_lsh_buckets(vector, model))
                        ],
                    )

                missing_count = int(connection.execute(
                    _RESOLVED_FILES_CTE + """
                    SELECT COUNT(*)
                    FROM resolved_files AS rf
                    JOIN artifact_documents AS d
                      ON d.artifact_id = rf.artifact_id
                    LEFT JOIN embeddings AS e
                      ON e.content_signature = d.content_signature
                     AND e.model = ?
                    WHERE e.content_signature IS NULL
                    """,
                    (head.snapshot_id, model),
                ).fetchone()[0])
                if missing_count:
                    raise RuntimeError(
                        f"enrichment revision is incomplete: {missing_count} documents missing"
                    )

                dimension_rows = connection.execute(
                    _RESOLVED_FILES_CTE + """
                    SELECT DISTINCT e.dimension
                    FROM resolved_files AS rf
                    JOIN artifact_documents AS d
                      ON d.artifact_id = rf.artifact_id
                    JOIN embeddings AS e
                      ON e.content_signature = d.content_signature
                     AND e.model = ?
                    """,
                    (head.snapshot_id, model),
                )
                stored_dimensions = {int(row[0]) for row in dimension_rows}
                if len(stored_dimensions) > 1:
                    raise RuntimeError("stored embeddings have inconsistent dimensions")
                dimension = next(iter(stored_dimensions), 0)
                revision = int(connection.execute(
                    """
                    SELECT COALESCE(MAX(revision), 0) + 1
                    FROM enrichment_revisions
                    WHERE repo_id = ? AND branch = ?
                    """,
                    (scope.repo, scope.branch),
                ).fetchone()[0])
                cursor = connection.execute(
                    """
                    INSERT INTO enrichment_revisions(
                        repo_id, branch, generation_id, revision, model,
                        dimension, coverage, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 1.0, ?)
                    """,
                    (
                        scope.repo,
                        scope.branch,
                        head.generation_id,
                        revision,
                        model,
                        dimension,
                        timestamp,
                    ),
                )
                revision_id = int(cursor.lastrowid)
                connection.execute(
                    """
                    INSERT INTO enrichment_heads(repo_id, branch, revision_id)
                    VALUES (?, ?, ?)
                    ON CONFLICT(repo_id, branch) DO UPDATE SET
                        revision_id = excluded.revision_id
                    """,
                    (scope.repo, scope.branch, revision_id),
                )
                completed = connection.execute(
                    """
                    UPDATE enrichment_jobs
                    SET status = 'completed', error = '', owner_token = '', updated_at = ?
                    WHERE generation_id = ? AND status = 'running'
                      AND owner_token = ?
                    """,
                    (timestamp, head.generation_id, owner_token),
                )
                if not completed.rowcount:
                    raise RepositoryIndexError(
                        "ENRICHMENT_STALE",
                        "enrichment ownership changed before publication",
                        phase="enrich",
                        target=_target(scope),
                        retryable=True,
                    )

            return EnrichmentReport(
                scope=scope,
                generation=head.generation,
                revision=revision,
                model=model,
                dimension=dimension,
                documents=len(rows),
                embedded_signatures=len(new_vectors),
                reused_signatures=max(
                    0,
                    len({str(row["content_signature"]) for row in rows})
                    - len(new_vectors),
                ),
                elapsed_ms=_elapsed_ms(started),
            )
        except RepositoryIndexError as error:
            self._mark_enrichment_failed(head.generation_id, owner_token, str(error))
            raise
        except Exception as error:
            self._mark_enrichment_failed(head.generation_id, owner_token, str(error))
            raise RepositoryIndexError(
                "ENRICHMENT_FAILED",
                str(error),
                phase="enrich",
                target=_target(scope),
                retryable=True,
            ) from error

    def search(self, request: SearchRequest) -> SearchResult:
        started = time.perf_counter()
        self._validate_scope(request.scope)
        query = request.query.strip()
        if not query:
            self._raise_invalid("query must not be empty", request.scope)
        if request.limit < 1 or request.limit > MAX_LIMIT:
            self._raise_invalid(f"limit must be between 1 and {MAX_LIMIT}", request.scope)
        related_limit = request.limit if request.related_limit is None else request.related_limit
        if related_limit < 0 or related_limit > MAX_LIMIT:
            self._raise_invalid(
                f"related_limit must be between 0 and {MAX_LIMIT}",
                request.scope,
            )

        retrieval_mode = request.retrieval.casefold().strip()
        if retrieval_mode not in RETRIEVAL_MODES:
            self._raise_invalid(
                f"retrieval must be one of {', '.join(sorted(RETRIEVAL_MODES))}",
                request.scope,
            )

        expected_dense: _DenseState | None = None
        query_vector: tuple[float, ...] | None = None
        degradations: list[str] = []
        if retrieval_mode != "local":
            provider = self._embedding_provider
            if provider is None:
                self._dense_unavailable(
                    retrieval_mode,
                    request.scope,
                    "dense_provider_unavailable",
                    degradations,
                )
            else:
                expected_dense = self._read_dense_state(request.scope)
                model = _provider_model(provider)
                if expected_dense is None:
                    self._dense_unavailable(
                        retrieval_mode,
                        request.scope,
                        "dense_not_ready",
                        degradations,
                    )
                elif expected_dense.model != model:
                    self._dense_unavailable(
                        retrieval_mode,
                        request.scope,
                        "dense_model_mismatch",
                        degradations,
                    )
                else:
                    try:
                        query_vector = _normalize_vector(provider.embed_query(query))
                    except Exception as error:
                        self._dense_unavailable(
                            retrieval_mode,
                            request.scope,
                            f"dense_query_failed:{type(error).__name__}",
                            degradations,
                        )
                    if (
                        query_vector is not None
                        and expected_dense.dimension
                        and len(query_vector) != expected_dense.dimension
                    ):
                        query_vector = None
                        self._dense_unavailable(
                            retrieval_mode,
                            request.scope,
                            "dense_dimension_mismatch",
                            degradations,
                        )

        for _attempt in range(3):
            dense_used = False
            with self._store.transaction() as connection:
                head = self._head(connection, request.scope)
                if not head:
                    raise RepositoryIndexError(
                        "INDEX_NOT_FOUND",
                        f"index not found for {_target(request.scope)}",
                        phase="query",
                        target=_target(request.scope),
                    )
                exact_rows = self._exact_candidates(
                    connection, head.snapshot_id, query, request.limit * 4
                )
                lexical_rows = self._lexical_candidates(
                    connection, head.snapshot_id, query, request.limit * 4
                )
                dense_rows: list[dict] = []
                if query_vector is not None and expected_dense is not None:
                    actual_dense = self._dense_state(
                        connection,
                        request.scope,
                        head.generation_id,
                    )
                    if (
                        actual_dense is None
                        or actual_dense.revision_id != expected_dense.revision_id
                    ):
                        self._dense_unavailable(
                            retrieval_mode,
                            request.scope,
                            "dense_snapshot_changed",
                            degradations,
                        )
                    else:
                        dense_rows = self._dense_candidates(
                            connection,
                            head.snapshot_id,
                            actual_dense,
                            query_vector,
                            request.limit * DENSE_CANDIDATE_MULTIPLIER,
                            scope=request.scope,
                        )
                        dense_used = True
                strong_exact_rows = [
                    row for row in exact_rows
                    if float(row.get("exact_score", 0.0)) >= 80.0
                ]
                if strong_exact_rows:
                    exact_rows = strong_exact_rows
                    exact_ids = {
                        row["component_id"] for row in strong_exact_rows
                    }
                    lexical_rows = [
                        row for row in lexical_rows
                        if row["component_id"] in exact_ids
                    ]
                    dense_rows = [
                        row for row in dense_rows
                        if row["component_id"] in exact_ids
                    ]
                matches = self._fuse_candidates(
                    exact_rows,
                    lexical_rows,
                    dense_rows,
                    request.limit,
                )
            if not matches or not related_limit:
                related = ()
                break
            expected_head = head
            if not self._ensure_relation_cache(expected_head.snapshot_id):
                continue
            with self._store.transaction() as connection:
                actual_head = self._head(connection, request.scope)
                if _head_identity(actual_head) != _head_identity(expected_head):
                    continue
                related = self._related_candidates(
                    connection,
                    expected_head.snapshot_id,
                    matches,
                    related_limit,
                )
                break
        else:
            raise RepositoryIndexError(
                "STORE_BUSY",
                "branch head changed repeatedly while resolving search results",
                phase="query",
                target=_target(request.scope),
                retryable=True,
            )

        return SearchResult(
            scope=request.scope,
            generation=head.generation,
            tree_id=head.tree_id,
            matches=matches,
            related=related,
            retrieval="hybrid" if dense_used else "local",
            degradations=tuple(dict.fromkeys(degradations)),
            elapsed_ms=_elapsed_ms(started),
        )

    def inspect(
        self,
        scope: IndexScope,
        *,
        resolve_relations: bool = True,
    ) -> IndexStatus:
        self._validate_scope(scope)
        with self._store.transaction() as connection:
            head = self._head(connection, scope)
            if not head:
                return IndexStatus(scope, False, None, "", 0, 0, 0)
            files = int(connection.execute(
                _RESOLVED_FILES_CTE + "SELECT COUNT(*) FROM resolved_files",
                (head.snapshot_id,),
            ).fetchone()[0])
            symbols = int(connection.execute(
                _RESOLVED_FILES_CTE + """
                SELECT COUNT(*)
                FROM resolved_files AS rf
                JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
                """,
                (head.snapshot_id,),
            ).fetchone()[0])
            cache_ready = connection.execute(
                "SELECT 1 FROM relation_cache_states WHERE snapshot_id = ?",
                (head.snapshot_id,),
            ).fetchone()
            relations = (
                int(connection.execute(
                    "SELECT COUNT(*) FROM snapshot_relations WHERE snapshot_id = ?",
                    (head.snapshot_id,),
                ).fetchone()[0])
                if cache_ready
                else (
                    len(self._relation_rows(connection, head.snapshot_id))
                    if resolve_relations
                    else 0
                )
            )
            dense = self._dense_state(connection, scope, head.generation_id)
            job = connection.execute(
                """
                SELECT status FROM enrichment_jobs
                WHERE generation_id = ?
                """,
                (head.generation_id,),
            ).fetchone()
            pending_jobs = int(connection.execute(
                """
                SELECT COUNT(*) FROM enrichment_jobs
                WHERE repo_id = ? AND branch = ?
                  AND status IN ('pending', 'running', 'failed')
                """,
                (scope.repo, scope.branch),
            ).fetchone()[0])
            if dense:
                dense_state = "ready"
            elif job:
                dense_state = job["status"]
            else:
                dense_state = "not_ready"
            return IndexStatus(
                scope=scope,
                exists=True,
                generation=head.generation,
                tree_id=head.tree_id,
                files=files,
                symbols=symbols,
                relations=relations,
                enrichment_revision=dense.revision if dense else None,
                dense_state=dense_state,
                pending_jobs=pending_jobs,
            )

    def integrity(self) -> IntegrityReport:
        """Check database pages and declared foreign-key relationships."""
        try:
            with self._store.transaction() as connection:
                row = connection.execute("PRAGMA integrity_check").fetchone()
                message = str(row[0]) if row else "integrity check returned no result"
                violations = len(list(connection.execute("PRAGMA foreign_key_check")))
        except sqlite3.Error as error:
            return IntegrityReport(False, str(error), 0)
        return IntegrityReport(message == "ok" and violations == 0, message, violations)

    def maintain(self, *, retain_generations: int = 2) -> MaintenanceReport:
        """Recover interrupted enrichment and collect unreachable index state."""
        if retain_generations < 1:
            raise ValueError("retain_generations must be at least 1")
        try:
            with self._store.transaction(write=True) as connection:
                counts = self._maintain_state(
                    connection,
                    retain_generations=retain_generations,
                    recover_running=True,
                    collect_orphans=True,
                )
                snapshot_roots: dict[str, list[str]] = {}
                for row in connection.execute(
                    """
                    SELECT r.source_root, g.tree_id
                    FROM repositories AS r
                    LEFT JOIN generations AS g ON g.repo_id = r.repo_id
                    ORDER BY r.source_root, g.tree_id
                    """
                ):
                    retained = snapshot_roots.setdefault(row["source_root"], [])
                    if row["tree_id"] is not None:
                        retained.append(row["tree_id"])
        except sqlite3.Error as error:
            raise RepositoryIndexError(
                "STORE_CORRUPT",
                str(error),
                phase="maintain",
            ) from error

        deleted_snapshot_objects = 0
        try:
            for source_root, tree_ids in snapshot_roots.items():
                with GitSnapshot(Path(source_root)) as snapshot:
                    deleted_snapshot_objects += snapshot.prune_snapshots(
                        tuple(dict.fromkeys(tree_ids))
                    )
        except GitSnapshotError as error:
            raise RepositoryIndexError(
                "SOURCE_UNAVAILABLE",
                str(error),
                phase="maintain",
                retryable=True,
            ) from error

        reclaimed_pages = self._store.compact()
        integrity = self.integrity()
        if not integrity.ok:
            raise RepositoryIndexError(
                "STORE_CORRUPT",
                integrity.message,
                phase="maintain",
            )
        return MaintenanceReport(
            retained_generations=retain_generations,
            recovered_jobs=counts.recovered_jobs,
            superseded_jobs=counts.superseded_jobs,
            deleted_generations=counts.deleted_generations,
            deleted_revisions=counts.deleted_revisions,
            deleted_artifacts=counts.deleted_artifacts,
            deleted_embeddings=counts.deleted_embeddings,
            deleted_buckets=counts.deleted_buckets,
            deleted_snapshots=counts.deleted_snapshots,
            deleted_snapshot_objects=deleted_snapshot_objects,
            reclaimed_pages=reclaimed_pages,
            integrity=integrity,
        )

    def reconcile_branches(
        self,
        repo: str,
        active_branches: Sequence[str],
    ) -> BranchReconcileReport:
        """Remove index scopes that are no longer active for a repository."""
        repo_id = repo.strip()
        if not repo_id:
            raise ValueError("repo must not be empty")
        active = tuple(dict.fromkeys(
            branch.strip() for branch in active_branches if branch.strip()
        ))
        with self._store.transaction(write=True) as connection:
            existing = tuple(
                str(row["branch"])
                for row in connection.execute(
                    """
                    SELECT branch FROM branch_heads
                    WHERE repo_id = ? ORDER BY branch
                    """,
                    (repo_id,),
                )
            )
            active_set = set(active)
            removed = tuple(branch for branch in existing if branch not in active_set)
            for branches in _chunks(removed):
                placeholders = ",".join("?" for _ in branches)
                params = (repo_id, *branches)
                connection.execute(
                    f"DELETE FROM branch_heads WHERE repo_id = ? "
                    f"AND branch IN ({placeholders})",
                    params,
                )
                connection.execute(
                    f"DELETE FROM generations WHERE repo_id = ? "
                    f"AND branch IN ({placeholders})",
                    params,
                )
            if removed:
                active_snapshot_ids = tuple(
                    int(row["snapshot_id"])
                    for row in connection.execute(
                        """
                        SELECT DISTINCT g.snapshot_id
                        FROM branch_heads AS h
                        JOIN generations AS g ON g.id = h.generation_id
                        WHERE h.repo_id = ?
                        """,
                        (repo_id,),
                    )
                )
                if len(active_snapshot_ids) == 1:
                    self._flatten_snapshot(connection, active_snapshot_ids[0])
            counts = self._maintain_state(
                connection,
                retain_generations=2,
                recover_running=False,
                collect_orphans=True,
            )
        reclaimed_pages = self._store.compact() if removed else 0
        return BranchReconcileReport(
            repo=repo_id,
            active_branches=active,
            removed_branches=removed,
            deleted_snapshots=counts.deleted_snapshots,
            deleted_artifacts=counts.deleted_artifacts,
            deleted_embeddings=counts.deleted_embeddings,
            reclaimed_pages=reclaimed_pages,
        )

    @staticmethod
    def _flatten_snapshot(
        connection: sqlite3.Connection,
        snapshot_id: int,
    ) -> None:
        row = connection.execute(
            "SELECT base_snapshot_id FROM snapshots WHERE id = ?",
            (snapshot_id,),
        ).fetchone()
        if not row or row["base_snapshot_id"] is None:
            return
        resolved = list(connection.execute(
            _RESOLVED_FILES_CTE
            + "SELECT path, path_key, blob_id, artifact_id FROM resolved_files",
            (snapshot_id,),
        ))
        connection.execute(
            "DELETE FROM snapshot_changes WHERE snapshot_id = ?",
            (snapshot_id,),
        )
        connection.executemany(
            """
            INSERT INTO snapshot_changes(
                snapshot_id, path, path_key, kind, blob_id, artifact_id
            ) VALUES (?, ?, ?, 'upsert', ?, ?)
            """,
            [
                (
                    snapshot_id,
                    item["path"],
                    item["path_key"],
                    item["blob_id"],
                    item["artifact_id"],
                )
                for item in resolved
            ],
        )
        connection.execute(
            """
            UPDATE snapshots
            SET base_snapshot_id = NULL, depth = 0
            WHERE id = ?
            """,
            (snapshot_id,),
        )
        connection.execute(
            """
            WITH RECURSIVE descendants(id, resolved_depth) AS (
                SELECT id, 0 FROM snapshots WHERE id = ?
                UNION ALL
                SELECT child.id, parent.resolved_depth + 1
                FROM snapshots AS child
                JOIN descendants AS parent
                  ON child.base_snapshot_id = parent.id
            )
            UPDATE snapshots
            SET depth = (
                SELECT resolved_depth FROM descendants
                WHERE descendants.id = snapshots.id
            )
            WHERE id IN (SELECT id FROM descendants)
            """,
            (snapshot_id,),
        )

    @staticmethod
    def _maintain_state(
        connection: sqlite3.Connection,
        *,
        retain_generations: int,
        recover_running: bool,
        collect_orphans: bool,
    ) -> _MaintenanceCounts:
        timestamp = _timestamp()
        recovered_jobs = 0
        superseded_jobs = 0
        current_generation_ids = {
            int(row[0])
            for row in connection.execute("SELECT generation_id FROM branch_heads")
        }
        if recover_running:
            lease_cutoff = (
                datetime.now(UTC) - timedelta(seconds=ENRICHMENT_LEASE_SECONDS)
            ).isoformat()
            for row in connection.execute(
                """
                SELECT generation_id FROM enrichment_jobs
                WHERE status = 'running' AND updated_at < ?
                """,
                (lease_cutoff,),
            ):
                generation_id = int(row["generation_id"])
                if generation_id in current_generation_ids:
                    connection.execute(
                        """
                        UPDATE enrichment_jobs
                        SET status = 'pending',
                            error = 'recovered interrupted enrichment',
                            owner_token = '',
                            updated_at = ?
                        WHERE generation_id = ?
                        """,
                        (timestamp, generation_id),
                    )
                    recovered_jobs += 1
                else:
                    connection.execute(
                        """
                        UPDATE enrichment_jobs
                        SET status = 'superseded',
                            error = 'superseded after interrupted enrichment',
                            owner_token = '',
                            updated_at = ?
                        WHERE generation_id = ?
                        """,
                        (timestamp, generation_id),
                    )
                    superseded_jobs += 1

        stale_generation_ids: list[int] = []
        generation_counts: dict[tuple[str, str], int] = {}
        for row in connection.execute(
            """
            SELECT id, repo_id, branch
            FROM generations
            ORDER BY repo_id, branch, generation DESC
            """
        ):
            key = (row["repo_id"], row["branch"])
            generation_counts[key] = generation_counts.get(key, 0) + 1
            generation_id = int(row["id"])
            if (
                generation_counts[key] > retain_generations
                and generation_id not in current_generation_ids
            ):
                stale_generation_ids.append(generation_id)

        stale_snapshot_ids: list[int] = []
        deleted_generations = 0
        deleted_revisions = 0
        for generation_ids in _chunks(tuple(stale_generation_ids)):
            placeholders = ",".join("?" for _ in generation_ids)
            stale_snapshot_ids.extend(
                int(row["snapshot_id"])
                for row in connection.execute(
                    f"SELECT snapshot_id FROM generations "
                    f"WHERE id IN ({placeholders})",
                    generation_ids,
                )
            )
            deleted_revisions += int(connection.execute(
                f"SELECT COUNT(*) FROM enrichment_revisions "
                f"WHERE generation_id IN ({placeholders})",
                generation_ids,
            ).fetchone()[0])
            connection.execute(
                f"UPDATE generations SET parent_id = NULL "
                f"WHERE parent_id IN ({placeholders})",
                generation_ids,
            )
            deleted_generations += connection.execute(
                f"DELETE FROM generations WHERE id IN ({placeholders})",
                generation_ids,
            ).rowcount

        deleted_buckets = 0
        deleted_embeddings = 0
        deleted_artifacts = 0
        deleted_snapshots = 0
        if collect_orphans:
            reachable_snapshot_ids = {
                int(row[0])
                for row in connection.execute(
                    """
                    WITH RECURSIVE reachable(id) AS (
                        SELECT DISTINCT snapshot_id FROM generations
                        UNION
                        SELECT s.base_snapshot_id
                        FROM snapshots AS s
                        JOIN reachable AS r ON r.id = s.id
                        WHERE s.base_snapshot_id IS NOT NULL
                    )
                    SELECT id FROM reachable
                    """
                )
            }
            stale_snapshots = [
                int(row["id"])
                for row in connection.execute(
                    "SELECT id FROM snapshots ORDER BY depth DESC, id DESC"
                )
                if int(row["id"]) not in reachable_snapshot_ids
            ]
            for snapshot_ids in _chunks(tuple(stale_snapshots)):
                placeholders = ",".join("?" for _ in snapshot_ids)
                deleted_snapshots += connection.execute(
                    f"DELETE FROM snapshots WHERE id IN ({placeholders})",
                    snapshot_ids,
                ).rowcount

            buckets_before = int(connection.execute(
                "SELECT COUNT(*) FROM embedding_buckets"
            ).fetchone()[0])
            deleted_artifacts = connection.execute(
                """
                DELETE FROM parse_artifacts
                WHERE NOT EXISTS (
                    SELECT 1 FROM snapshot_changes AS sc
                    WHERE sc.artifact_id = parse_artifacts.artifact_id
                )
                """
            ).rowcount
            deleted_embeddings = connection.execute(
                """
                DELETE FROM embeddings
                WHERE NOT EXISTS (
                    SELECT 1 FROM artifact_documents AS d
                    WHERE d.content_signature = embeddings.content_signature
                )
                """
            ).rowcount
            buckets_after = int(connection.execute(
                "SELECT COUNT(*) FROM embedding_buckets"
            ).fetchone()[0])
            deleted_buckets = max(0, buckets_before - buckets_after)
        elif stale_snapshot_ids:
            reachable_snapshot_ids = {
                int(row[0])
                for row in connection.execute(
                    """
                    WITH RECURSIVE reachable(id) AS (
                        SELECT DISTINCT snapshot_id FROM generations
                        UNION
                        SELECT s.base_snapshot_id
                        FROM snapshots AS s
                        JOIN reachable AS r ON r.id = s.id
                        WHERE s.base_snapshot_id IS NOT NULL
                    )
                    SELECT id FROM reachable
                    """
                )
            }
            candidate_snapshot_ids: set[int] = set()
            for snapshot_ids in _chunks(tuple(dict.fromkeys(stale_snapshot_ids))):
                placeholders = ",".join("?" for _ in snapshot_ids)
                candidate_snapshot_ids.update(
                    int(row[0])
                    for row in connection.execute(
                        f"""
                        WITH RECURSIVE candidates(id) AS (
                            SELECT id FROM snapshots
                            WHERE id IN ({placeholders})
                            UNION
                            SELECT s.base_snapshot_id
                            FROM snapshots AS s
                            JOIN candidates AS c ON c.id = s.id
                            WHERE s.base_snapshot_id IS NOT NULL
                        )
                        SELECT id FROM candidates
                        """,
                        snapshot_ids,
                    )
                )
            candidate_depths: dict[int, int] = {}
            for snapshot_ids in _chunks(tuple(candidate_snapshot_ids)):
                placeholders = ",".join("?" for _ in snapshot_ids)
                candidate_depths.update({
                    int(row["id"]): int(row["depth"])
                    for row in connection.execute(
                        f"SELECT id, depth FROM snapshots "
                        f"WHERE id IN ({placeholders})",
                        snapshot_ids,
                    )
                })
            stale_snapshots = tuple(sorted(
                (
                    snapshot_id
                    for snapshot_id in candidate_snapshot_ids
                    if snapshot_id not in reachable_snapshot_ids
                ),
                key=lambda snapshot_id: (
                    candidate_depths.get(snapshot_id, -1),
                    snapshot_id,
                ),
                reverse=True,
            ))
            artifact_candidates: set[str] = set()
            for snapshot_ids in _chunks(stale_snapshots):
                placeholders = ",".join("?" for _ in snapshot_ids)
                artifact_candidates.update(
                    str(row[0])
                    for row in connection.execute(
                        f"""
                        SELECT DISTINCT artifact_id FROM snapshot_changes
                        WHERE snapshot_id IN ({placeholders})
                          AND artifact_id IS NOT NULL
                        """,
                        snapshot_ids,
                    )
                )
                deleted_snapshots += connection.execute(
                    f"DELETE FROM snapshots WHERE id IN ({placeholders})",
                    snapshot_ids,
                ).rowcount

            signature_candidates: set[str] = set()
            for artifact_ids in _chunks(tuple(artifact_candidates)):
                placeholders = ",".join("?" for _ in artifact_ids)
                signature_candidates.update(
                    str(row[0])
                    for row in connection.execute(
                        f"""
                        SELECT DISTINCT content_signature
                        FROM artifact_documents
                        WHERE artifact_id IN ({placeholders})
                        """,
                        artifact_ids,
                    )
                )
                deleted_artifacts += connection.execute(
                    f"""
                    DELETE FROM parse_artifacts
                    WHERE artifact_id IN ({placeholders})
                      AND NOT EXISTS (
                          SELECT 1 FROM snapshot_changes AS sc
                          WHERE sc.artifact_id = parse_artifacts.artifact_id
                      )
                    """,
                    artifact_ids,
                ).rowcount

            for signatures in _chunks(tuple(signature_candidates)):
                placeholders = ",".join("?" for _ in signatures)
                deleted_buckets += int(connection.execute(
                    f"""
                    SELECT COUNT(*) FROM embedding_buckets AS b
                    WHERE b.content_signature IN ({placeholders})
                      AND NOT EXISTS (
                          SELECT 1 FROM artifact_documents AS d
                          WHERE d.content_signature = b.content_signature
                      )
                    """,
                    signatures,
                ).fetchone()[0])
                deleted_embeddings += connection.execute(
                    f"""
                    DELETE FROM embeddings
                    WHERE content_signature IN ({placeholders})
                      AND NOT EXISTS (
                          SELECT 1 FROM artifact_documents AS d
                          WHERE d.content_signature = embeddings.content_signature
                      )
                    """,
                    signatures,
                ).rowcount
        return _MaintenanceCounts(
            recovered_jobs=recovered_jobs,
            superseded_jobs=superseded_jobs,
            deleted_generations=deleted_generations,
            deleted_revisions=deleted_revisions,
            deleted_artifacts=deleted_artifacts,
            deleted_embeddings=deleted_embeddings,
            deleted_buckets=deleted_buckets,
            deleted_snapshots=deleted_snapshots,
        )

    def symbols(
        self,
        scope: IndexScope,
        *,
        component_ids: Sequence[str] = (),
        paths: Sequence[str] = (),
    ) -> tuple[SymbolRecord, ...]:
        """Return the current generation's structural symbol projection."""
        self._validate_scope(scope)
        ids = tuple(dict.fromkeys(component_ids))
        selected_paths = tuple(dict.fromkeys(paths))

        def read_symbols(
            connection: sqlite3.Connection,
            head: _Head,
        ) -> tuple[SymbolRecord, ...]:
            clauses = ["1 = 1"]
            params: list[object] = [head.snapshot_id]
            selectors: list[str] = []
            if ids:
                selectors.append(
                    f"(rf.path || '::' || s.local_id) "
                    f"IN ({','.join('?' for _ in ids)})"
                )
                params.extend(ids)
            if selected_paths:
                selectors.append(
                    f"rf.path IN ({','.join('?' for _ in selected_paths)})"
                )
                params.extend(selected_paths)
            if selectors:
                clauses.append(f"({' OR '.join(selectors)})")
            rows = list(connection.execute(
                _RESOLVED_FILES_CTE + f"""
                SELECT
                    rf.path || '::' || s.local_id AS component_id,
                    rf.path AS path,
                    s.symbol,
                    s.kind,
                    s.line_start, s.line_end, s.docstring, s.source,
                    s.imports_json, s.entry_point_kind, s.entry_point_path
                FROM resolved_files AS rf
                JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
                WHERE {' AND '.join(clauses)}
                ORDER BY rf.path, s.line_start, component_id
                """,
                params,
            ))
            return self._symbol_records(connection, head.snapshot_id, rows)

        return self._read_relation_snapshot(scope, read_symbols) or ()

    def files(self, scope: IndexScope) -> tuple[str, ...]:
        """Return source paths visible from the current branch head."""
        self._validate_scope(scope)
        with self._store.transaction() as connection:
            head = self._head(connection, scope)
            if not head:
                return ()
            return tuple(
                str(row["path"])
                for row in connection.execute(
                    _RESOLVED_FILES_CTE
                    + "SELECT path FROM resolved_files ORDER BY path",
                    (head.snapshot_id,),
                )
            )

    def _read_relation_snapshot(
        self,
        scope: IndexScope,
        reader: Callable[[sqlite3.Connection, _Head], _T],
    ) -> _T | None:
        for _attempt in range(3):
            expected_head = self._read_head(scope)
            if not expected_head:
                return None
            if not self._ensure_relation_cache(expected_head.snapshot_id):
                continue
            with self._store.transaction() as connection:
                head = self._head(connection, scope)
                if _head_identity(head) != _head_identity(expected_head):
                    continue
                if not head:
                    return None
                return reader(connection, head)
        raise RepositoryIndexError(
            "STORE_BUSY",
            "branch head changed repeatedly while preparing relation cache",
            phase="query",
            target=_target(scope),
            retryable=True,
        )

    def trace(
        self,
        scope: IndexScope,
        component_id: str,
        *,
        direction: str = "down",
        max_depth: int = 3,
    ) -> tuple[SymbolRecord, ...]:
        """Traverse the current generation's resolved call graph breadth-first."""
        self._validate_scope(scope)
        if direction not in {"up", "down"}:
            self._raise_invalid("direction must be 'up' or 'down'", scope)
        depth_limit = max(0, min(max_depth, 8))

        def read_trace(
            connection: sqlite3.Connection,
            head: _Head,
        ) -> tuple[SymbolRecord, ...]:
            exists = connection.execute(
                _RESOLVED_FILES_CTE + """
                SELECT 1
                FROM resolved_files AS rf
                JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
                WHERE rf.path || '::' || s.local_id = ?
                """,
                (head.snapshot_id, component_id),
            ).fetchone()
            if not exists:
                return ()

            ordered = [component_id]
            visited = {component_id}
            frontier = [component_id]
            for _ in range(depth_limit):
                if not frontier:
                    break
                placeholders = ",".join("?" for _ in frontier)
                if direction == "down":
                    query = (
                        "SELECT caller_id AS source_id, callee_id AS target_id "
                        "FROM snapshot_relations WHERE snapshot_id = ? "
                        f"AND caller_id IN ({placeholders}) ORDER BY caller_id, callee_id"
                    )
                else:
                    query = (
                        "SELECT callee_id AS source_id, caller_id AS target_id "
                        "FROM snapshot_relations WHERE snapshot_id = ? "
                        f"AND callee_id IN ({placeholders}) ORDER BY callee_id, caller_id"
                    )
                next_frontier: list[str] = []
                for row in connection.execute(query, (head.snapshot_id, *frontier)):
                    target = str(row["target_id"])
                    if target in visited:
                        continue
                    visited.add(target)
                    ordered.append(target)
                    next_frontier.append(target)
                frontier = next_frontier

            placeholders = ",".join("?" for _ in ordered)
            rows_by_id = {
                row["component_id"]: row
                for row in connection.execute(
                    _RESOLVED_FILES_CTE + f"""
                    SELECT
                        rf.path || '::' || s.local_id AS component_id,
                        rf.path AS path,
                        s.symbol,
                        s.kind,
                        s.line_start, s.line_end, s.docstring, s.source,
                        s.imports_json, s.entry_point_kind, s.entry_point_path
                    FROM resolved_files AS rf
                    JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
                    WHERE rf.path || '::' || s.local_id IN ({placeholders})
                    """,
                    (head.snapshot_id, *ordered),
                )
            }
            rows = [rows_by_id[item] for item in ordered if item in rows_by_id]
            return self._symbol_records(connection, head.snapshot_id, rows)

        return self._read_relation_snapshot(scope, read_trace) or ()

    def _symbol_records(
        self,
        connection: sqlite3.Connection,
        snapshot_id: int,
        rows: Sequence[sqlite3.Row],
    ) -> tuple[SymbolRecord, ...]:
        ids = tuple(str(row["component_id"]) for row in rows)
        calls: dict[str, list[str]] = {item: [] for item in ids}
        called_by: dict[str, list[str]] = {item: [] for item in ids}
        for chunk in _chunks(ids):
            placeholders = ",".join("?" for _ in chunk)
            for relation in connection.execute(
                f"""
                SELECT caller_id, callee_id FROM snapshot_relations
                WHERE snapshot_id = ?
                  AND (caller_id IN ({placeholders}) OR callee_id IN ({placeholders}))
                ORDER BY caller_id, callee_id
                """,
                (snapshot_id, *chunk, *chunk),
            ):
                caller = str(relation["caller_id"])
                callee = str(relation["callee_id"])
                if caller in calls:
                    calls[caller].append(callee)
                if callee in called_by:
                    called_by[callee].append(caller)
        return tuple(
            SymbolRecord(
                component_id=str(row["component_id"]),
                file=str(row["path"]),
                symbol=str(row["symbol"]),
                type=str(row["kind"]),
                line_start=int(row["line_start"]),
                line_end=int(row["line_end"]),
                docstring=str(row["docstring"]),
                source=str(row["source"]),
                imports=tuple(json.loads(row["imports_json"] or "[]")),
                calls=tuple(dict.fromkeys(calls[str(row["component_id"])])),
                called_by=tuple(dict.fromkeys(called_by[str(row["component_id"])])),
                entry_point_kind=str(row["entry_point_kind"]),
                entry_point_path=str(row["entry_point_path"]),
            )
            for row in rows
        )

    def _prepare_artifacts(
        self,
        snapshot: GitSnapshot,
        entries: tuple[TreeEntry, ...],
    ) -> _PreparedArtifacts:
        entry_artifacts = {
            entry.path: _artifact_id(entry.blob_id, _context_hash(entry.path))
            for entry in entries
        }
        artifact_ids = tuple(dict.fromkeys(entry_artifacts.values()))
        existing = self._load_artifacts(artifact_ids)
        missing: dict[str, TreeEntry] = {}
        for entry in entries:
            artifact_id = entry_artifacts[entry.path]
            if artifact_id not in existing:
                missing.setdefault(artifact_id, entry)

        blobs = snapshot.read_blobs([entry.blob_id for entry in missing.values()])
        new_payloads: dict[str, tuple[str, str, str, str]] = {}
        with tempfile.TemporaryDirectory(prefix="repo-wiki-parse-") as temp_dir:
            temp_root = Path(temp_dir)
            for artifact_id, entry in missing.items():
                suffix = PurePosixPath(entry.path).suffix.lower()
                materialized = temp_root / f"source-{artifact_id}{suffix}"
                source = blobs[entry.blob_id]
                materialized.write_bytes(source)
                try:
                    nodes = parse_file(materialized, temp_root, strict=True)
                except Exception as error:
                    raise RepositoryIndexError(
                        "PARSE_FAILED",
                        f"{entry.path}: {error}",
                        phase="parse",
                    ) from error
                payload = json.dumps(
                    _canonical_nodes(nodes),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                context_hash = _context_hash(entry.path)
                new_payloads[artifact_id] = (
                    entry.blob_id,
                    PARSER_VERSION,
                    context_hash,
                    payload,
                )

        payloads = dict(existing)
        payloads.update({key: value[3] for key, value in new_payloads.items()})
        return _PreparedArtifacts(
            entry_artifacts=entry_artifacts,
            payloads=payloads,
            new_payloads=new_payloads,
            parsed_blobs=len(missing),
            reused_blobs=max(0, len(entries) - len(missing)),
        )

    def _select_snapshot_base(
        self,
        snapshot: GitSnapshot,
        repo: str,
        tree_id: str,
        head: _Head | None,
        logical_delta: TreeDelta,
    ) -> tuple[_SnapshotRef | None, TreeDelta]:
        candidates: list[_SnapshotRef] = []
        if head:
            current = self._read_snapshot_by_id(head.snapshot_id)
            if current:
                candidates.append(current)
        for candidate in self._snapshot_candidates(repo):
            if candidate.snapshot_id not in {
                item.snapshot_id for item in candidates
            }:
                candidates.append(candidate)

        best: tuple[int, _SnapshotRef, TreeDelta] | None = None
        for candidate in candidates:
            if candidate.depth >= MAX_SNAPSHOT_DEPTH - 1:
                continue
            delta = snapshot.delta(candidate.tree_id, tree_id)
            cost = len(delta.changed) + len(delta.removed)
            if best is None or (cost, candidate.depth) < (best[0], best[1].depth):
                best = (cost, candidate, delta)
                if cost <= 1:
                    break

        if best and best[0] <= 1:
            return best[1], best[2]
        if head is None:
            full_delta = logical_delta
        else:
            full_delta = snapshot.initial_delta(tree_id)
        full_cost = len(full_delta.changed)
        if best and best[0] < full_cost:
            return best[1], best[2]
        return None, full_delta

    def _read_snapshot(self, repo: str, tree_id: str) -> _SnapshotRef | None:
        with self._store.transaction() as connection:
            row = connection.execute(
                """
                SELECT id, tree_id, depth FROM snapshots
                WHERE repo_id = ? AND tree_id = ?
                """,
                (repo, tree_id),
            ).fetchone()
        return _snapshot_ref(row)

    def _read_snapshot_by_id(self, snapshot_id: int) -> _SnapshotRef | None:
        with self._store.transaction() as connection:
            row = connection.execute(
                "SELECT id, tree_id, depth FROM snapshots WHERE id = ?",
                (snapshot_id,),
            ).fetchone()
        return _snapshot_ref(row)

    def _snapshot_candidates(self, repo: str) -> tuple[_SnapshotRef, ...]:
        with self._store.transaction() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT s.id, s.tree_id, s.depth
                FROM branch_heads AS h
                JOIN generations AS g ON g.id = h.generation_id
                JOIN snapshots AS s ON s.id = g.snapshot_id
                WHERE h.repo_id = ?
                ORDER BY s.depth, s.id DESC
                LIMIT 16
                """,
                (repo,),
            )
            return tuple(
                candidate
                for row in rows
                if (candidate := _snapshot_ref(row)) is not None
            )

    def _load_artifacts(self, artifact_ids: tuple[str, ...]) -> dict[str, str]:
        if not artifact_ids:
            return {}
        result: dict[str, str] = {}
        with self._store.transaction() as connection:
            for chunk in _chunks(artifact_ids):
                placeholders = ",".join("?" for _ in chunk)
                rows = connection.execute(
                    f"SELECT artifact_id, payload_json FROM parse_artifacts "
                    f"WHERE artifact_id IN ({placeholders})",
                    chunk,
                )
                result.update({row["artifact_id"]: row["payload_json"] for row in rows})
        return result

    def _load_embedding_vectors(
        self,
        signatures: tuple[str, ...],
        model: str,
    ) -> dict[str, tuple[float, ...]]:
        if not signatures:
            return {}
        result: dict[str, tuple[float, ...]] = {}
        with self._store.transaction() as connection:
            for chunk in _chunks(signatures):
                placeholders = ",".join("?" for _ in chunk)
                rows = connection.execute(
                    f"""
                    SELECT content_signature, dimension, vector
                    FROM embeddings
                    WHERE model = ? AND content_signature IN ({placeholders})
                    """,
                    (model, *chunk),
                )
                for row in rows:
                    result[row["content_signature"]] = _unpack_vector(
                        row["vector"],
                        int(row["dimension"]),
                    )
        return result

    @staticmethod
    def _document_count(
        connection: sqlite3.Connection,
        snapshot_id: int,
    ) -> int:
        return int(connection.execute(
            _RESOLVED_FILES_CTE + """
            SELECT COUNT(*)
            FROM resolved_files AS rf
            JOIN artifact_documents AS d ON d.artifact_id = rf.artifact_id
            """,
            (snapshot_id,),
        ).fetchone()[0])

    def _mark_enrichment_failed(
        self,
        generation_id: int,
        owner_token: str,
        message: str,
    ) -> None:
        try:
            with self._store.transaction(write=True) as connection:
                connection.execute(
                    """
                    UPDATE enrichment_jobs
                    SET status = 'failed', error = ?, owner_token = '', updated_at = ?
                    WHERE generation_id = ? AND status = 'running'
                      AND owner_token = ?
                    """,
                    (message[:500], _timestamp(), generation_id, owner_token),
                )
        except sqlite3.Error:
            return

    def _read_dense_state(self, scope: IndexScope) -> _DenseState | None:
        with self._store.transaction() as connection:
            head = self._head(connection, scope)
            if not head:
                return None
            return self._dense_state(connection, scope, head.generation_id)

    @staticmethod
    def _dense_state(
        connection: sqlite3.Connection,
        scope: IndexScope,
        generation_id: int,
    ) -> _DenseState | None:
        row = connection.execute(
            """
            SELECT
                r.id AS revision_id,
                r.revision,
                r.model,
                r.dimension
            FROM enrichment_heads AS h
            JOIN enrichment_revisions AS r ON r.id = h.revision_id
            WHERE h.repo_id = ? AND h.branch = ?
              AND r.generation_id = ? AND r.coverage = 1.0
            """,
            (scope.repo, scope.branch, generation_id),
        ).fetchone()
        if not row:
            return None
        return _DenseState(
            generation_id=generation_id,
            revision_id=int(row["revision_id"]),
            revision=int(row["revision"]),
            model=row["model"],
            dimension=int(row["dimension"]),
        )

    @staticmethod
    def _dense_unavailable(
        retrieval_mode: str,
        scope: IndexScope,
        reason: str,
        degradations: list[str],
    ) -> None:
        if retrieval_mode == "required":
            raise RepositoryIndexError(
                "HYBRID_REQUIRED_UNAVAILABLE",
                reason,
                phase="query",
                target=_target(scope),
                retryable=True,
            )
        degradations.append(reason)

    def _dense_candidates(
        self,
        connection: sqlite3.Connection,
        snapshot_id: int,
        state: _DenseState,
        query_vector: tuple[float, ...],
        limit: int,
        *,
        scope: IndexScope,
    ) -> list[dict]:
        if state.dimension == 0:
            return []
        if len(query_vector) != state.dimension:
            raise RepositoryIndexError(
                "INVARIANT_VIOLATION",
                "query and document embedding dimensions differ",
                phase="query",
                target=_target(scope),
            )
        buckets = tuple(enumerate(_lsh_buckets(query_vector, state.model)))
        values = ",".join("(?, ?)" for _ in buckets)
        bucket_params = tuple(value for pair in buckets for value in pair)
        rows = connection.execute(
            _RESOLVED_FILES_CTE + f""",
            query_buckets(table_no, bucket) AS (VALUES {values})
            SELECT b.content_signature, COUNT(DISTINCT b.table_no) AS bucket_matches
            FROM embedding_buckets AS b
            JOIN query_buckets AS q
              ON q.table_no = b.table_no AND q.bucket = b.bucket
            JOIN artifact_documents AS d
              ON d.content_signature = b.content_signature
            JOIN resolved_files AS rf ON rf.artifact_id = d.artifact_id
            WHERE b.model = ?
            GROUP BY b.content_signature
            ORDER BY bucket_matches DESC, b.content_signature
            LIMIT ?
            """,
            (snapshot_id, *bucket_params, state.model, limit),
        )
        candidate_signatures = tuple(row["content_signature"] for row in rows)
        if not candidate_signatures:
            return []

        candidates = []
        for chunk in _chunks(candidate_signatures):
            placeholders = ",".join("?" for _ in chunk)
            vector_rows = connection.execute(
                _RESOLVED_FILES_CTE + f"""
                SELECT
                    rf.path || '::' || s.local_id AS component_id,
                    rf.path AS path,
                    s.symbol,
                    s.kind,
                    s.line_start, s.line_end, s.source,
                    e.dimension, e.vector
                FROM resolved_files AS rf
                JOIN artifact_documents AS d
                  ON d.artifact_id = rf.artifact_id
                JOIN artifact_symbols AS s
                  ON s.artifact_id = d.artifact_id
                 AND s.local_id = d.local_id
                JOIN embeddings AS e
                  ON e.content_signature = d.content_signature
                 AND e.model = ?
                WHERE d.content_signature IN ({placeholders})
                """,
                (snapshot_id, state.model, *chunk),
            )
            for row in vector_rows:
                vector = _unpack_vector(row["vector"], int(row["dimension"]))
                similarity = sum(
                    left * right
                    for left, right in zip(query_vector, vector, strict=True)
                )
                item = dict(row)
                item.pop("dimension", None)
                item.pop("vector", None)
                item["dense_score"] = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
                candidates.append(item)
        return sorted(
            candidates,
            key=lambda item: (-item["dense_score"], item["component_id"]),
        )[:limit]

    def _publish_generation(
        self,
        *,
        scope: IndexScope,
        source_root: Path,
        tree_id: str,
        expected_head: _Head | None,
        delta: TreeDelta,
        snapshot_delta: TreeDelta,
        snapshot_base: _SnapshotRef | None,
        existing_snapshot: _SnapshotRef | None,
        prepared: _PreparedArtifacts,
        parsed_blobs: int,
        reused_blobs: int,
    ) -> int:
        timestamp = _timestamp()
        with self._store.transaction(write=True) as connection:
            actual_head = self._head(connection, scope)
            if _head_identity(actual_head) != _head_identity(expected_head):
                raise RepositoryIndexError(
                    "SYNC_CONFLICT",
                    f"head changed while synchronizing {_target(scope)}",
                    phase="commit",
                    target=_target(scope),
                    retryable=True,
                )

            connection.execute(
                """
                INSERT INTO repositories(repo_id, source_root, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(repo_id) DO UPDATE SET
                    source_root = excluded.source_root,
                    updated_at = excluded.updated_at
                """,
                (scope.repo, str(source_root), timestamp, timestamp),
            )
            for artifact_id, values in prepared.new_payloads.items():
                connection.execute(
                    """
                    INSERT OR IGNORE INTO parse_artifacts(
                        artifact_id, blob_id, parser_version, context_hash,
                        payload_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (artifact_id, *values, timestamp),
                )
                self._insert_artifact_records(
                    connection,
                    artifact_id,
                    prepared.payloads[artifact_id],
                )

            for label, snapshot_ref in (
                ("reused snapshot", existing_snapshot),
                ("overlay base", snapshot_base),
            ):
                if snapshot_ref is None:
                    continue
                snapshot_row = connection.execute(
                    """
                    SELECT repo_id, tree_id FROM snapshots WHERE id = ?
                    """,
                    (snapshot_ref.snapshot_id,),
                ).fetchone()
                if (
                    not snapshot_row
                    or snapshot_row["repo_id"] != scope.repo
                    or snapshot_row["tree_id"] != snapshot_ref.tree_id
                ):
                    raise RepositoryIndexError(
                        "SYNC_CONFLICT",
                        f"{label} was reclaimed while synchronizing {_target(scope)}",
                        phase="commit",
                        target=_target(scope),
                        retryable=True,
                    )

            required_artifacts = set(prepared.entry_artifacts.values())
            visible_artifacts: set[str] = set()
            for artifact_ids in _chunks(tuple(required_artifacts)):
                placeholders = ",".join("?" for _ in artifact_ids)
                visible_artifacts.update(
                    str(row[0])
                    for row in connection.execute(
                        f"SELECT artifact_id FROM parse_artifacts "
                        f"WHERE artifact_id IN ({placeholders})",
                        artifact_ids,
                    )
                )
            if visible_artifacts != required_artifacts:
                raise RepositoryIndexError(
                    "SYNC_CONFLICT",
                    f"cached artifacts were reclaimed while synchronizing {_target(scope)}",
                    phase="commit",
                    target=_target(scope),
                    retryable=True,
                )

            snapshot_id = (
                existing_snapshot.snapshot_id if existing_snapshot is not None else None
            )
            if snapshot_id is None:
                snapshot_insert = connection.execute(
                    """
                    INSERT OR IGNORE INTO snapshots(
                        repo_id, tree_id, base_snapshot_id, depth, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        scope.repo,
                        tree_id,
                        snapshot_base.snapshot_id if snapshot_base else None,
                        snapshot_base.depth + 1 if snapshot_base else 0,
                        timestamp,
                    ),
                )
                snapshot_row = connection.execute(
                    "SELECT id FROM snapshots WHERE repo_id = ? AND tree_id = ?",
                    (scope.repo, tree_id),
                ).fetchone()
                if not snapshot_row:
                    raise RuntimeError("snapshot insert did not publish a visible row")
                snapshot_id = int(snapshot_row["id"])
                if snapshot_insert.rowcount:
                    connection.executemany(
                        """
                        INSERT INTO snapshot_changes(
                            snapshot_id, path, path_key, kind, blob_id, artifact_id
                        ) VALUES (?, ?, ?, 'upsert', ?, ?)
                        """,
                        [
                            (
                                snapshot_id,
                                entry.path,
                                _key(entry.path),
                                entry.blob_id,
                                prepared.entry_artifacts[entry.path],
                            )
                            for entry in snapshot_delta.changed
                        ],
                    )
                    connection.executemany(
                        """
                        INSERT INTO snapshot_changes(
                            snapshot_id, path, path_key, kind, blob_id, artifact_id
                        ) VALUES (?, ?, ?, 'delete', NULL, NULL)
                        """,
                        [
                            (snapshot_id, path, _key(path))
                            for path in snapshot_delta.removed
                        ],
                    )

            generation = 1 if actual_head is None else actual_head.generation + 1
            cursor = connection.execute(
                """
                INSERT INTO generations(
                    repo_id, branch, generation, tree_id, snapshot_id,
                    parent_id, created_at,
                    changed_count, removed_count, parsed_count, reused_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scope.repo,
                    scope.branch,
                    generation,
                    tree_id,
                    snapshot_id,
                    actual_head.generation_id if actual_head else None,
                    timestamp,
                    len(delta.changed),
                    len(delta.removed),
                    parsed_blobs,
                    reused_blobs,
                ),
            )
            generation_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO generation_changes(generation_id, path, kind, blob_id)
                VALUES (?, ?, 'upsert', ?)
                """,
                [(generation_id, entry.path, entry.blob_id) for entry in delta.changed],
            )
            connection.executemany(
                """
                INSERT INTO generation_changes(generation_id, path, kind, blob_id)
                VALUES (?, ?, 'delete', NULL)
                """,
                [(generation_id, path) for path in delta.removed],
            )
            connection.execute(
                """
                INSERT INTO branch_heads(repo_id, branch, generation_id)
                VALUES (?, ?, ?)
                ON CONFLICT(repo_id, branch) DO UPDATE SET
                    generation_id = excluded.generation_id
                """,
                (scope.repo, scope.branch, generation_id),
            )
            connection.execute(
                "DELETE FROM enrichment_heads WHERE repo_id = ? AND branch = ?",
                (scope.repo, scope.branch),
            )
            connection.execute(
                """
                UPDATE enrichment_jobs
                SET status = 'superseded', owner_token = '', updated_at = ?
                WHERE repo_id = ? AND branch = ?
                  AND status IN ('pending', 'running', 'failed')
                """,
                (timestamp, scope.repo, scope.branch),
            )
            connection.execute(
                """
                INSERT INTO enrichment_jobs(
                    repo_id, branch, generation_id, status, attempts,
                    error, created_at, updated_at
                ) VALUES (?, ?, ?, 'pending', 0, '', ?, ?)
                """,
                (scope.repo, scope.branch, generation_id, timestamp, timestamp),
            )
            self._maintain_state(
                connection,
                retain_generations=2,
                recover_running=False,
                collect_orphans=False,
            )
            return generation

    @staticmethod
    def _insert_artifact_records(
        connection: sqlite3.Connection,
        artifact_id: str,
        payload: str,
    ) -> None:
        for record in json.loads(payload):
            local_id = str(record["local_id"])
            symbol = local_id
            short_name = local_id.rsplit(".", 1)[-1]
            imports = [str(value) for value in record.get("imports", [])]
            calls = sorted({str(value) for value in record.get("calls", []) if value})
            docstring = str(record.get("docstring") or "")
            source = str(record.get("source") or "")
            kind = str(record.get("type") or "symbol")
            connection.execute(
                """
                INSERT OR IGNORE INTO artifact_symbols(
                    artifact_id, local_id, symbol, symbol_key,
                    short_name, short_key, kind, line_start, line_end,
                    docstring, source, imports_json,
                    entry_point_kind, entry_point_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    local_id,
                    symbol,
                    _key(symbol),
                    short_name,
                    _key(short_name),
                    kind,
                    int(record.get("line_start", 0)),
                    int(record.get("line_end", 0)),
                    docstring,
                    source,
                    json.dumps(imports, ensure_ascii=False, separators=(",", ":")),
                    str(record.get("entry_point_kind") or ""),
                    str(record.get("entry_point_path") or ""),
                ),
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO artifact_calls(
                    artifact_id, local_id, call_name, call_key
                ) VALUES (?, ?, ?, ?)
                """,
                [
                    (artifact_id, local_id, call, _key(call))
                    for call in calls
                ],
            )
            text = "\n".join(part for part in (
                local_id,
                symbol,
                docstring,
                source,
                " ".join(calls),
                " ".join(imports),
            ) if part)
            connection.execute(
                """
                INSERT OR IGNORE INTO artifact_documents(
                    artifact_id, local_id, symbol, kind, text, content_signature
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    local_id,
                    symbol,
                    kind,
                    text,
                    hashlib.sha256(text.encode()).hexdigest(),
                ),
            )

    def _ensure_relation_cache(self, snapshot_id: int) -> bool:
        try:
            with self._store.transaction() as connection:
                ready = connection.execute(
                    "SELECT 1 FROM relation_cache_states WHERE snapshot_id = ?",
                    (snapshot_id,),
                ).fetchone()
                if ready:
                    return True
                exists = connection.execute(
                    "SELECT 1 FROM snapshots WHERE id = ?",
                    (snapshot_id,),
                ).fetchone()
                if not exists:
                    return False
                relations = self._relation_rows(connection, snapshot_id)

            with self._store.transaction(write=True) as connection:
                ready = connection.execute(
                    "SELECT 1 FROM relation_cache_states WHERE snapshot_id = ?",
                    (snapshot_id,),
                ).fetchone()
                if ready:
                    return True
                exists = connection.execute(
                    "SELECT 1 FROM snapshots WHERE id = ?",
                    (snapshot_id,),
                ).fetchone()
                if not exists:
                    return False
                connection.executemany(
                    """
                    INSERT OR IGNORE INTO snapshot_relations(
                        snapshot_id, caller_id, callee_id, kind
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        (snapshot_id, caller_id, callee_id, kind)
                        for caller_id, callee_id, kind in relations
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO relation_cache_states(snapshot_id, created_at)
                    VALUES (?, ?)
                    """,
                    (snapshot_id, _timestamp()),
                )
            return True
        except sqlite3.OperationalError as error:
            if "locked" in str(error).casefold():
                raise RepositoryIndexError(
                    "STORE_BUSY",
                    str(error),
                    phase="query",
                    target=f"snapshot:{snapshot_id}",
                    retryable=True,
                ) from error
            raise

    @staticmethod
    def _relation_rows(
        connection: sqlite3.Connection,
        snapshot_id: int,
    ) -> tuple[tuple[str, str, str], ...]:
        symbols = list(connection.execute(
            _RESOLVED_FILES_CTE + """
            SELECT
                rf.path,
                s.local_id,
                s.short_key,
                rf.path || '::' || s.local_id AS component_id
            FROM resolved_files AS rf
            JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
            ORDER BY component_id
            """,
            (snapshot_id,),
        ))
        targets_by_name: dict[str, list[sqlite3.Row]] = {}
        for symbol in symbols:
            targets_by_name.setdefault(str(symbol["short_key"]), []).append(symbol)
        calls = connection.execute(
            _RESOLVED_FILES_CTE + """
            SELECT
                rf.path,
                rf.path || '::' || c.local_id AS caller_id,
                c.call_key,
                caller.imports_json
            FROM resolved_files AS rf
            JOIN artifact_calls AS c ON c.artifact_id = rf.artifact_id
            JOIN artifact_symbols AS caller
              ON caller.artifact_id = c.artifact_id
             AND caller.local_id = c.local_id
            ORDER BY caller_id, c.call_key
            """,
            (snapshot_id,),
        )
        targets_by_module: dict[tuple[str, str], list[sqlite3.Row]] = {}
        for symbol in symbols:
            for module_key in _path_module_keys(str(symbol["path"])):
                targets_by_module.setdefault(
                    (str(symbol["short_key"]), module_key),
                    [],
                ).append(symbol)

        relations: set[tuple[str, str, str]] = set()
        import_cache: dict[tuple[str, str], tuple[str, ...]] = {}
        for call in calls:
            targets = targets_by_name.get(str(call["call_key"]), [])
            same_file = [
                target for target in targets
                if target["path"] == call["path"]
            ]
            caller_id = str(call["caller_id"])
            call_key = str(call["call_key"])
            if same_file:
                resolved_targets = same_file
            else:
                cache_key = (caller_id, call_key)
                module_keys = import_cache.get(cache_key)
                if module_keys is None:
                    module_keys = _import_module_keys(
                        str(call["imports_json"]),
                        call_key,
                    )
                    import_cache[cache_key] = module_keys
                imported: dict[str, sqlite3.Row] = {}
                for module_key in module_keys:
                    for target in targets_by_module.get(
                        (call_key, module_key),
                        (),
                    ):
                        imported[str(target["component_id"])] = target
                resolved_targets = (
                    list(imported.values())
                    if imported
                    else (targets if len(targets) == 1 else [])
                )
            for target in resolved_targets:
                relations.add((
                    caller_id,
                    str(target["component_id"]),
                    "call",
                ))
        return tuple(sorted(relations))

    def _exact_candidates(
        self,
        connection: sqlite3.Connection,
        snapshot_id: int,
        query: str,
        limit: int,
    ) -> list[dict]:
        query_key = _key(query)
        rows = connection.execute(
            _RESOLVED_FILES_CTE + """
            SELECT
                rf.path || '::' || s.local_id AS component_id,
                rf.path AS path,
                s.symbol,
                s.kind,
                s.line_start, s.line_end, s.source,
                CASE
                    WHEN rf.path_key || '::' || s.symbol_key = ? THEN 100.0
                    WHEN s.symbol_key = ? THEN 90.0
                    WHEN s.short_key = ? THEN 85.0
                    WHEN rf.path_key = ? THEN 80.0
                    WHEN instr(rf.path_key, ?) > 0 THEN 60.0
                    ELSE 0.0
                END AS exact_score
            FROM resolved_files AS rf
            JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
            WHERE (
                  rf.path_key || '::' || s.symbol_key = ? OR
                  s.symbol_key = ? OR s.short_key = ? OR rf.path_key = ? OR
                  instr(rf.path_key, ?) > 0
              )
            ORDER BY exact_score DESC, component_id
            LIMIT ?
            """,
            (
                snapshot_id,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                query_key,
                limit,
            ),
        )
        return [dict(row) for row in rows]

    def _lexical_candidates(
        self,
        connection: sqlite3.Connection,
        snapshot_id: int,
        query: str,
        limit: int,
    ) -> list[dict]:
        expression = _fts_expression(query)
        if not expression:
            return []
        try:
            rows = connection.execute(
                _RESOLVED_FILES_CTE + """
                SELECT
                    rf.path || '::' || s.local_id AS component_id,
                    rf.path AS path,
                    s.symbol,
                    s.kind,
                    s.line_start, s.line_end, s.source,
                    bm25(artifact_documents_fts, 5.0, 1.0) AS lexical_rank
                FROM artifact_documents_fts
                JOIN artifact_documents AS d
                  ON d.id = artifact_documents_fts.rowid
                JOIN resolved_files AS rf ON rf.artifact_id = d.artifact_id
                JOIN artifact_symbols AS s
                  ON s.artifact_id = d.artifact_id
                 AND s.local_id = d.local_id
                WHERE artifact_documents_fts MATCH ?
                ORDER BY lexical_rank, component_id
                LIMIT ?
                """,
                (snapshot_id, expression, limit),
            )
            result = []
            for row in rows:
                item = dict(row)
                item["lexical_score"] = max(0.0, -float(item.pop("lexical_rank")))
                result.append(item)
            return result
        except sqlite3.OperationalError as error:
            if "fts5" in str(error).casefold() or "syntax" in str(error).casefold():
                raise RepositoryIndexError(
                    "INVARIANT_VIOLATION",
                    str(error),
                    phase="query",
                    target=f"snapshot:{snapshot_id}",
                ) from error
            raise

    def _fuse_candidates(
        self,
        exact_rows: list[dict],
        lexical_rows: list[dict],
        dense_rows: list[dict],
        limit: int,
    ) -> tuple[SearchHit, ...]:
        candidates: dict[str, dict] = {}
        for channel, rows in (
            ("exact", exact_rows),
            ("lexical", lexical_rows),
            ("dense", dense_rows),
        ):
            for rank, row in enumerate(rows, start=1):
                candidate = candidates.setdefault(row["component_id"], {
                    **row,
                    "exact": 0.0,
                    "lexical": 0.0,
                    "dense": 0.0,
                    "rrf": 0.0,
                })
                candidate.update({key: value for key, value in row.items() if key not in candidate})
                candidate[channel] = float(row.get(f"{channel}_score", 0.0))
                candidate["rrf"] += 1.0 / (RRF_K + rank)

        for candidate in candidates.values():
            exact_boost = candidate["exact"] / 100.0
            lexical_boost = min(1.0, candidate["lexical"])
            dense_boost = max(0.0, min(1.0, candidate["dense"]))
            candidate["final"] = (
                candidate["rrf"]
                + exact_boost
                + lexical_boost * 0.1
                + dense_boost * 0.1
            )

        ordered = sorted(
            candidates.values(),
            key=lambda item: (-item["final"], -item["exact"], item["component_id"]),
        )[:limit]
        return tuple(_search_hit(item) for item in ordered)

    def _related_candidates(
        self,
        connection: sqlite3.Connection,
        snapshot_id: int,
        matches: tuple[SearchHit, ...],
        limit: int,
    ) -> tuple[SearchHit, ...]:
        if not matches or limit == 0:
            return ()
        direct = {hit.component_id for hit in matches}
        ranks = {
            hit.component_id: rank
            for rank, hit in enumerate(matches, start=1)
        }
        related_scores: dict[str, float] = {}
        for chunk in _chunks(tuple(ranks)):
            placeholders = ",".join("?" for _ in chunk)
            rows = connection.execute(
                f"""
                SELECT caller_id, callee_id
                FROM snapshot_relations
                WHERE snapshot_id = ?
                  AND (
                    caller_id IN ({placeholders})
                    OR callee_id IN ({placeholders})
                  )
                ORDER BY caller_id, callee_id
                """,
                (snapshot_id, *chunk, *chunk),
            )
            for row in rows:
                for source, neighbor in (
                    (str(row["caller_id"]), str(row["callee_id"])),
                    (str(row["callee_id"]), str(row["caller_id"])),
                ):
                    rank = ranks.get(source)
                    if rank is None or neighbor in direct:
                        continue
                    related_scores[neighbor] = max(
                        related_scores.get(neighbor, 0.0),
                        1.0 / rank,
                    )

        ordered_ids = sorted(related_scores, key=lambda item: (-related_scores[item], item))[:limit]
        if not ordered_ids:
            return ()
        rows_by_id: dict[str, sqlite3.Row] = {}
        for chunk in _chunks(tuple(ordered_ids)):
            placeholders = ",".join("?" for _ in chunk)
            rows = connection.execute(
                _RESOLVED_FILES_CTE + f"""
                SELECT
                    rf.path || '::' || s.local_id AS component_id,
                    rf.path AS path,
                    s.symbol,
                    s.kind,
                    s.line_start,
                    s.line_end,
                    s.source
                FROM resolved_files AS rf
                JOIN artifact_symbols AS s ON s.artifact_id = rf.artifact_id
                WHERE rf.path || '::' || s.local_id IN ({placeholders})
                """,
                (snapshot_id, *chunk),
            )
            rows_by_id.update({row["component_id"]: row for row in rows})

        result = []
        for component_id in ordered_ids:
            row = rows_by_id.get(component_id)
            if not row:
                continue
            graph_score = related_scores[component_id]
            result.append(SearchHit(
                component_id=component_id,
                file=row["path"],
                symbol=row["symbol"],
                type=row["kind"],
                line_start=int(row["line_start"]),
                line_end=int(row["line_end"]),
                source=row["source"],
                score=graph_score,
                score_breakdown={
                    "exact": 0.0,
                    "lexical": 0.0,
                    "dense": 0.0,
                    "rrf": 0.0,
                    "graph": graph_score,
                    "final": graph_score,
                },
            ))
        return tuple(result)

    def _read_head(self, scope: IndexScope) -> _Head | None:
        with self._store.transaction() as connection:
            return self._head(connection, scope)

    @staticmethod
    def _head(connection: sqlite3.Connection, scope: IndexScope) -> _Head | None:
        row = connection.execute(
            """
            SELECT g.id, g.generation, g.tree_id, g.snapshot_id
            FROM branch_heads AS h
            JOIN generations AS g ON g.id = h.generation_id
            WHERE h.repo_id = ? AND h.branch = ?
            """,
            (scope.repo, scope.branch),
        ).fetchone()
        if not row:
            return None
        return _Head(
            generation_id=int(row["id"]),
            generation=int(row["generation"]),
            tree_id=row["tree_id"],
            snapshot_id=int(row["snapshot_id"]),
        )

    @staticmethod
    def _validate_scope(scope: IndexScope) -> None:
        if not scope.repo.strip():
            raise RepositoryIndexError(
                "INVALID_REQUEST",
                "repo must not be empty",
                phase="validate",
            )
        if not scope.branch.strip():
            raise RepositoryIndexError(
                "INVALID_REQUEST",
                "branch must not be empty",
                phase="validate",
                target=scope.repo,
            )

    @staticmethod
    def _raise_invalid(message: str, scope: IndexScope) -> None:
        raise RepositoryIndexError(
            "INVALID_REQUEST",
            message,
            phase="validate",
            target=_target(scope),
        )


def _canonical_nodes(nodes: list[ASTNode]) -> list[dict]:
    result: list[dict] = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, ASTNode):
            raise TypeError(f"parser returned unsupported node {type(node).__name__}")
        local_id = node.id.split("::", 1)[-1]
        if not local_id or local_id in seen:
            continue
        seen.add(local_id)
        record = asdict(node)
        record.pop("id", None)
        record.pop("file", None)
        record.pop("called_by", None)
        record["local_id"] = local_id
        result.append(record)
    return sorted(result, key=lambda item: (item["local_id"], item["line_start"]))


def _artifact_id(blob_id: str, context_hash: str) -> str:
    value = f"{blob_id}\0{PARSER_VERSION}\0{context_hash}".encode()
    return hashlib.sha256(value).hexdigest()


def _context_hash(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    return hashlib.sha256(f"{suffix}\0{PARSER_VERSION}".encode()).hexdigest()[:16]


def _path_module_keys(path: str) -> tuple[str, ...]:
    source_path = PurePosixPath(path)
    without_suffix = str(source_path.with_suffix(""))
    parts = [part for part in without_suffix.replace("\\", "/").split("/") if part]
    if parts and parts[-1] == "__init__":
        parts.pop()
    return tuple(dict.fromkeys(
        _key(".".join(parts[index:]))
        for index in range(len(parts))
    ))


def _import_module_keys(imports_json: str, call_key: str) -> tuple[str, ...]:
    result: list[str] = []
    for value in json.loads(imports_json or "[]"):
        normalized = _key(str(value)).replace("::", ".").replace("/", ".")
        parts = [part for part in normalized.split(".") if part]
        if len(parts) > 1 and parts[-1] == call_key:
            parts.pop()
        result.extend(
            ".".join(parts[index:])
            for index in range(len(parts))
        )
    return tuple(dict.fromkeys(result))


def _fts_expression(query: str) -> str:
    tokens = re.findall(r"[^\W_]+(?:_[^\W_]+)*", query.casefold(), flags=re.UNICODE)
    return " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)


def _search_hit(candidate: dict) -> SearchHit:
    breakdown = {
        "exact": float(candidate.get("exact", 0.0)),
        "lexical": float(candidate.get("lexical", 0.0)),
        "dense": float(candidate.get("dense", 0.0)),
        "rrf": float(candidate.get("rrf", 0.0)),
        "graph": 0.0,
        "final": float(candidate.get("final", 0.0)),
    }
    return SearchHit(
        component_id=candidate["component_id"],
        file=candidate["path"],
        symbol=candidate["symbol"],
        type=candidate["kind"],
        line_start=int(candidate["line_start"]),
        line_end=int(candidate["line_end"]),
        source=candidate["source"],
        score=breakdown["final"],
        score_breakdown=breakdown,
    )


def _chunks(values: Sequence[object], size: int = 400) -> Iterable[tuple[object, ...]]:
    for start in range(0, len(values), size):
        yield tuple(values[start:start + size])


def _head_identity(head: _Head | None) -> tuple[int, str] | None:
    return None if head is None else (head.generation_id, head.tree_id)


def _snapshot_ref(row: sqlite3.Row | None) -> _SnapshotRef | None:
    if row is None:
        return None
    return _SnapshotRef(
        snapshot_id=int(row["id"]),
        tree_id=str(row["tree_id"]),
        depth=int(row["depth"]),
    )


def _key(value: str) -> str:
    return value.casefold()


def _provider_model(provider: EmbeddingProvider) -> str:
    model = str(provider.model).strip()
    if not model:
        raise RepositoryIndexError(
            "ENRICHMENT_UNAVAILABLE",
            "embedding provider model must not be empty",
            phase="enrich",
        )
    return model


def _normalize_vector(values: Sequence[float]) -> tuple[float, ...]:
    vector = tuple(float(value) for value in values)
    if not vector or any(not math.isfinite(value) for value in vector):
        raise ValueError("embedding vector must contain finite values")
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise ValueError("embedding vector must not be zero")
    return tuple(value / norm for value in vector)


def _pack_vector(vector: tuple[float, ...]) -> bytes:
    return array("f", vector).tobytes()


def _unpack_vector(payload: bytes, dimension: int) -> tuple[float, ...]:
    values = array("f")
    values.frombytes(payload)
    if len(values) != dimension:
        raise ValueError(
            f"stored embedding dimension mismatch: expected {dimension}, got {len(values)}"
        )
    return tuple(float(value) for value in values)


def _lsh_buckets(vector: tuple[float, ...], model: str) -> tuple[int, ...]:
    if not vector:
        return ()
    result = []
    for table_no in range(LSH_TABLES):
        bucket = 0
        for bit in range(LSH_BITS):
            digest = hashlib.sha256(f"{model}\0{table_no}\0{bit}".encode()).digest()
            coordinate = int.from_bytes(digest[:8], "big") % len(vector)
            if vector[coordinate] >= 0:
                bucket |= 1 << bit
        result.append(bucket)
    return tuple(result)


def _target(scope: IndexScope) -> str:
    return f"{scope.repo}:{scope.branch}"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)


__all__ = [
    "BranchReconcileReport",
    "EmbeddingProvider",
    "EnrichmentReport",
    "IndexScope",
    "IndexStatus",
    "IntegrityReport",
    "MaintenanceReport",
    "RepositoryIndex",
    "RepositoryIndexError",
    "SearchHit",
    "SearchRequest",
    "SearchResult",
    "SymbolRecord",
    "SyncReport",
    "SyncRequest",
]
