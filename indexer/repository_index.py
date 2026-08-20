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
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Iterable, Protocol, Sequence

from indexer.ast_parser import ASTNode, parse_file
from indexer.git_snapshot import GitSnapshot, GitSnapshotError, TreeDelta, TreeEntry
from indexer.repository_store import RepositoryStore, RepositoryStoreError


PARSER_VERSION = "semantic-ast-v1"
RRF_K = 60
MAX_LIMIT = 100
LSH_TABLES = 8
LSH_BITS = 10
DENSE_CANDIDATE_MULTIPLIER = 8
RETRIEVAL_MODES = frozenset({"local", "preferred", "required"})


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
    deleted_snapshot_objects: int
    integrity: IntegrityReport


@dataclass(frozen=True)
class _Head:
    generation_id: int
    generation: int
    tree_id: str


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
                delta = (
                    snapshot.delta(head.tree_id, tree_id)
                    if head
                    else snapshot.initial_delta(tree_id)
                )
                prepared = self._prepare_artifacts(snapshot, delta.changed)
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

        try:
            generation = self._publish_generation(
                scope=scope,
                source_root=request.root.resolve(),
                tree_id=tree_id,
                expected_head=head,
                delta=delta,
                prepared=prepared,
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

        return SyncReport(
            status="published",
            repo=scope.repo,
            branch=scope.branch,
            generation=generation,
            tree_id=tree_id,
            changed_files=tuple(entry.path for entry in delta.changed),
            removed_files=delta.removed,
            parsed_blobs=prepared.parsed_blobs,
            reused_blobs=prepared.reused_blobs,
            tree_entries_scanned=delta.entries_scanned,
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
                documents = _count(connection, "documents", scope)
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
            connection.execute(
                """
                UPDATE enrichment_jobs
                SET status = 'running', attempts = attempts + 1,
                    error = '', updated_at = ?
                WHERE generation_id = ?
                """,
                (timestamp, head.generation_id),
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
                    """
                    SELECT
                        d.component_id, d.text, d.content_signature,
                        de.content_signature AS mapped_signature,
                        de.model AS mapped_model
                    FROM documents AS d
                    LEFT JOIN document_embeddings AS de
                      ON de.repo_id = d.repo_id
                     AND de.branch = d.branch
                     AND de.component_id = d.component_id
                    WHERE d.repo_id = ? AND d.branch = ?
                    ORDER BY d.component_id
                    """,
                    (scope.repo, scope.branch),
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

                for row in missing_documents:
                    component_id = row["component_id"]
                    signature = row["content_signature"]
                    vector = vectors[signature]
                    connection.execute(
                        """
                        DELETE FROM embedding_buckets
                        WHERE repo_id = ? AND branch = ? AND component_id = ?
                        """,
                        (scope.repo, scope.branch, component_id),
                    )
                    connection.execute(
                        """
                        DELETE FROM document_embeddings
                        WHERE repo_id = ? AND branch = ? AND component_id = ?
                        """,
                        (scope.repo, scope.branch, component_id),
                    )
                    connection.execute(
                        """
                        INSERT INTO document_embeddings(
                            repo_id, branch, component_id, content_signature, model
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (scope.repo, scope.branch, component_id, signature, model),
                    )
                    connection.executemany(
                        """
                        INSERT INTO embedding_buckets(
                            repo_id, branch, component_id, model, table_no, bucket
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (
                                scope.repo,
                                scope.branch,
                                component_id,
                                model,
                                table_no,
                                bucket,
                            )
                            for table_no, bucket in enumerate(_lsh_buckets(vector, model))
                        ],
                    )

                missing_count = int(connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM documents AS d
                    LEFT JOIN document_embeddings AS de
                      ON de.repo_id = d.repo_id
                     AND de.branch = d.branch
                     AND de.component_id = d.component_id
                     AND de.content_signature = d.content_signature
                     AND de.model = ?
                    WHERE d.repo_id = ? AND d.branch = ?
                      AND de.component_id IS NULL
                    """,
                    (model, scope.repo, scope.branch),
                ).fetchone()[0])
                if missing_count:
                    raise RuntimeError(
                        f"enrichment revision is incomplete: {missing_count} documents missing"
                    )

                dimension_rows = connection.execute(
                    """
                    SELECT DISTINCT e.dimension
                    FROM documents AS d
                    JOIN document_embeddings AS de
                      ON de.repo_id = d.repo_id
                     AND de.branch = d.branch
                     AND de.component_id = d.component_id
                     AND de.content_signature = d.content_signature
                     AND de.model = ?
                    JOIN embeddings AS e
                      ON e.content_signature = de.content_signature
                     AND e.model = de.model
                    WHERE d.repo_id = ? AND d.branch = ?
                    """,
                    (model, scope.repo, scope.branch),
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
                connection.execute(
                    """
                    UPDATE enrichment_jobs
                    SET status = 'completed', error = '', updated_at = ?
                    WHERE generation_id = ?
                    """,
                    (timestamp, head.generation_id),
                )

            return EnrichmentReport(
                scope=scope,
                generation=head.generation,
                revision=revision,
                model=model,
                dimension=dimension,
                documents=len(rows),
                embedded_signatures=len(new_vectors),
                reused_signatures=len(cached_vectors),
                elapsed_ms=_elapsed_ms(started),
            )
        except RepositoryIndexError as error:
            self._mark_enrichment_failed(head.generation_id, str(error))
            raise
        except Exception as error:
            self._mark_enrichment_failed(head.generation_id, str(error))
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
            exact_rows = self._exact_candidates(connection, request.scope, query, request.limit * 4)
            lexical_rows = self._lexical_candidates(connection, request.scope, query, request.limit * 4)
            dense_rows: list[dict] = []
            if query_vector is not None and expected_dense is not None:
                actual_dense = self._dense_state(connection, request.scope, head.generation_id)
                if actual_dense is None or actual_dense.revision_id != expected_dense.revision_id:
                    self._dense_unavailable(
                        retrieval_mode,
                        request.scope,
                        "dense_snapshot_changed",
                        degradations,
                    )
                else:
                    dense_rows = self._dense_candidates(
                        connection,
                        request.scope,
                        actual_dense,
                        query_vector,
                        request.limit * DENSE_CANDIDATE_MULTIPLIER,
                    )
                    dense_used = True
            if exact_rows:
                exact_ids = {row["component_id"] for row in exact_rows}
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
            related = self._related_candidates(
                connection,
                request.scope,
                matches,
                related_limit,
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

    def inspect(self, scope: IndexScope) -> IndexStatus:
        self._validate_scope(scope)
        with self._store.transaction() as connection:
            head = self._head(connection, scope)
            if not head:
                return IndexStatus(scope, False, None, "", 0, 0, 0)
            files = _count(connection, "files", scope)
            symbols = _count(connection, "symbols", scope)
            relations = _count(connection, "relations", scope)
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
                    FROM generations AS g
                    JOIN repositories AS r ON r.repo_id = g.repo_id
                    ORDER BY r.source_root, g.tree_id
                    """
                ):
                    snapshot_roots.setdefault(row["source_root"], []).append(
                        row["tree_id"]
                    )
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
            deleted_snapshot_objects=deleted_snapshot_objects,
            integrity=integrity,
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
            for row in connection.execute(
                "SELECT generation_id FROM enrichment_jobs WHERE status = 'running'"
            ):
                generation_id = int(row["generation_id"])
                if generation_id in current_generation_ids:
                    connection.execute(
                        """
                        UPDATE enrichment_jobs
                        SET status = 'pending',
                            error = 'recovered interrupted enrichment',
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

        deleted_generations = 0
        deleted_revisions = 0
        for generation_ids in _chunks(tuple(stale_generation_ids)):
            placeholders = ",".join("?" for _ in generation_ids)
            revision_ids = tuple(
                int(row[0])
                for row in connection.execute(
                    f"""
                    SELECT id FROM enrichment_revisions
                    WHERE generation_id IN ({placeholders})
                    """,
                    generation_ids,
                )
            )
            if revision_ids:
                revision_placeholders = ",".join("?" for _ in revision_ids)
                connection.execute(
                    f"""
                    DELETE FROM enrichment_heads
                    WHERE revision_id IN ({revision_placeholders})
                    """,
                    revision_ids,
                )
            deleted_revisions += connection.execute(
                f"""
                DELETE FROM enrichment_revisions
                WHERE generation_id IN ({placeholders})
                """,
                generation_ids,
            ).rowcount
            connection.execute(
                f"DELETE FROM enrichment_jobs WHERE generation_id IN ({placeholders})",
                generation_ids,
            )
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
        if collect_orphans:
            deleted_buckets = connection.execute(
                """
                DELETE FROM embedding_buckets
                WHERE NOT EXISTS (
                    SELECT 1 FROM document_embeddings AS de
                    WHERE de.repo_id = embedding_buckets.repo_id
                      AND de.branch = embedding_buckets.branch
                      AND de.component_id = embedding_buckets.component_id
                      AND de.model = embedding_buckets.model
                )
                """
            ).rowcount
            deleted_embeddings = connection.execute(
                """
                DELETE FROM embeddings
                WHERE NOT EXISTS (
                    SELECT 1 FROM document_embeddings AS de
                    WHERE de.content_signature = embeddings.content_signature
                      AND de.model = embeddings.model
                )
                """
            ).rowcount
            deleted_artifacts = connection.execute(
                """
                DELETE FROM parse_artifacts
                WHERE NOT EXISTS (
                    SELECT 1 FROM files
                    WHERE files.artifact_id = parse_artifacts.artifact_id
                )
                """
            ).rowcount
        return _MaintenanceCounts(
            recovered_jobs=recovered_jobs,
            superseded_jobs=superseded_jobs,
            deleted_generations=deleted_generations,
            deleted_revisions=deleted_revisions,
            deleted_artifacts=deleted_artifacts,
            deleted_embeddings=deleted_embeddings,
            deleted_buckets=deleted_buckets,
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
        with self._store.transaction() as connection:
            if not self._head(connection, scope):
                return ()
            clauses = ["s.repo_id = ?", "s.branch = ?"]
            params: list[object] = [scope.repo, scope.branch]
            selectors: list[str] = []
            if ids:
                selectors.append(f"s.component_id IN ({','.join('?' for _ in ids)})")
                params.extend(ids)
            if selected_paths:
                selectors.append(f"s.path IN ({','.join('?' for _ in selected_paths)})")
                params.extend(selected_paths)
            if selectors:
                clauses.append(f"({' OR '.join(selectors)})")
            rows = list(connection.execute(
                f"""
                SELECT
                    s.component_id, s.path, s.symbol, s.kind,
                    s.line_start, s.line_end, s.docstring, s.source,
                    s.imports_json, s.entry_point_kind, s.entry_point_path
                FROM symbols AS s
                WHERE {' AND '.join(clauses)}
                ORDER BY s.path, s.line_start, s.component_id
                """,
                params,
            ))
            return self._symbol_records(connection, scope, rows)

    def files(self, scope: IndexScope) -> tuple[str, ...]:
        """Return source paths visible from the current branch head."""
        self._validate_scope(scope)
        with self._store.transaction() as connection:
            if not self._head(connection, scope):
                return ()
            return tuple(
                str(row["path"])
                for row in connection.execute(
                    """
                    SELECT path FROM files
                    WHERE repo_id = ? AND branch = ?
                    ORDER BY path
                    """,
                    (scope.repo, scope.branch),
                )
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
        with self._store.transaction() as connection:
            if not self._head(connection, scope):
                return ()
            exists = connection.execute(
                """
                SELECT 1 FROM symbols
                WHERE repo_id = ? AND branch = ? AND component_id = ?
                """,
                (scope.repo, scope.branch, component_id),
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
                        "FROM relations WHERE repo_id = ? AND branch = ? "
                        f"AND caller_id IN ({placeholders}) ORDER BY caller_id, callee_id"
                    )
                else:
                    query = (
                        "SELECT callee_id AS source_id, caller_id AS target_id "
                        "FROM relations WHERE repo_id = ? AND branch = ? "
                        f"AND callee_id IN ({placeholders}) ORDER BY callee_id, caller_id"
                    )
                next_frontier: list[str] = []
                for row in connection.execute(query, (scope.repo, scope.branch, *frontier)):
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
                    f"""
                    SELECT
                        s.component_id, s.path, s.symbol, s.kind,
                        s.line_start, s.line_end, s.docstring, s.source,
                        s.imports_json, s.entry_point_kind, s.entry_point_path
                    FROM symbols AS s
                    WHERE s.repo_id = ? AND s.branch = ?
                      AND s.component_id IN ({placeholders})
                    """,
                    (scope.repo, scope.branch, *ordered),
                )
            }
            rows = [rows_by_id[item] for item in ordered if item in rows_by_id]
            return self._symbol_records(connection, scope, rows)

    def _symbol_records(
        self,
        connection: sqlite3.Connection,
        scope: IndexScope,
        rows: Sequence[sqlite3.Row],
    ) -> tuple[SymbolRecord, ...]:
        ids = tuple(str(row["component_id"]) for row in rows)
        calls: dict[str, list[str]] = {item: [] for item in ids}
        called_by: dict[str, list[str]] = {item: [] for item in ids}
        for chunk in _chunks(ids):
            placeholders = ",".join("?" for _ in chunk)
            for relation in connection.execute(
                f"""
                SELECT caller_id, callee_id FROM relations
                WHERE repo_id = ? AND branch = ?
                  AND (caller_id IN ({placeholders}) OR callee_id IN ({placeholders}))
                ORDER BY caller_id, callee_id
                """,
                (scope.repo, scope.branch, *chunk, *chunk),
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

    def _mark_enrichment_failed(self, generation_id: int, message: str) -> None:
        try:
            with self._store.transaction(write=True) as connection:
                connection.execute(
                    """
                    UPDATE enrichment_jobs
                    SET status = 'failed', error = ?, updated_at = ?
                    WHERE generation_id = ? AND status = 'running'
                    """,
                    (message[:500], _timestamp(), generation_id),
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
        scope: IndexScope,
        state: _DenseState,
        query_vector: tuple[float, ...],
        limit: int,
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
            f"""
            WITH query_buckets(table_no, bucket) AS (VALUES {values})
            SELECT b.component_id, COUNT(*) AS bucket_matches
            FROM embedding_buckets AS b
            JOIN query_buckets AS q
              ON q.table_no = b.table_no AND q.bucket = b.bucket
            WHERE b.repo_id = ? AND b.branch = ? AND b.model = ?
            GROUP BY b.component_id
            ORDER BY bucket_matches DESC, b.component_id
            LIMIT ?
            """,
            (*bucket_params, scope.repo, scope.branch, state.model, limit),
        )
        candidate_ids = tuple(row["component_id"] for row in rows)
        if not candidate_ids:
            return []

        candidates = []
        for chunk in _chunks(candidate_ids):
            placeholders = ",".join("?" for _ in chunk)
            vector_rows = connection.execute(
                f"""
                SELECT
                    s.component_id, s.path, s.symbol, s.kind,
                    s.line_start, s.line_end, s.source,
                    e.dimension, e.vector
                FROM symbols AS s
                JOIN document_embeddings AS de
                  ON de.repo_id = s.repo_id
                 AND de.branch = s.branch
                 AND de.component_id = s.component_id
                 AND de.model = ?
                JOIN embeddings AS e
                  ON e.content_signature = de.content_signature
                 AND e.model = de.model
                WHERE s.repo_id = ? AND s.branch = ?
                  AND s.component_id IN ({placeholders})
                """,
                (state.model, scope.repo, scope.branch, *chunk),
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
        prepared: _PreparedArtifacts,
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

            touched_paths = tuple(entry.path for entry in delta.changed) + delta.removed
            (
                old_components,
                old_names,
                old_artifacts,
                old_embeddings,
            ) = self._delete_paths(connection, scope, touched_paths)
            new_components, new_names = self._insert_entries(
                connection,
                scope,
                delta.changed,
                prepared,
            )
            self._delete_orphan_candidates(
                connection,
                artifact_ids=old_artifacts,
                embedding_keys=old_embeddings,
            )
            self._rebuild_relations(
                connection,
                scope,
                affected_names=old_names | new_names,
                changed_components=new_components,
                removed_components=old_components,
            )

            generation = 1 if actual_head is None else actual_head.generation + 1
            cursor = connection.execute(
                """
                INSERT INTO generations(
                    repo_id, branch, generation, tree_id, parent_id, created_at,
                    changed_count, removed_count, parsed_count, reused_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scope.repo,
                    scope.branch,
                    generation,
                    tree_id,
                    actual_head.generation_id if actual_head else None,
                    timestamp,
                    len(delta.changed),
                    len(delta.removed),
                    prepared.parsed_blobs,
                    prepared.reused_blobs,
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
                SET status = 'superseded', updated_at = ?
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

    def _delete_paths(
        self,
        connection: sqlite3.Connection,
        scope: IndexScope,
        paths: tuple[str, ...],
    ) -> tuple[set[str], set[str], set[str], set[tuple[str, str]]]:
        old_components: set[str] = set()
        old_names: set[str] = set()
        old_artifacts: set[str] = set()
        old_embeddings: set[tuple[str, str]] = set()
        for chunk in _chunks(paths):
            placeholders = ",".join("?" for _ in chunk)
            params = (scope.repo, scope.branch, *chunk)
            rows = connection.execute(
                f"""
                SELECT component_id, short_name
                FROM symbols
                WHERE repo_id = ? AND branch = ? AND path IN ({placeholders})
                """,
                params,
            )
            for row in rows:
                old_components.add(row["component_id"])
                old_names.add(row["short_name"])
            old_artifacts.update(
                row["artifact_id"]
                for row in connection.execute(
                    f"""
                    SELECT artifact_id FROM files
                    WHERE repo_id = ? AND branch = ?
                      AND path IN ({placeholders})
                    """,
                    params,
                )
            )
            old_embeddings.update(
                (row["content_signature"], row["model"])
                for row in connection.execute(
                    f"""
                    SELECT de.content_signature, de.model
                    FROM document_embeddings AS de
                    JOIN documents AS d
                      ON d.repo_id = de.repo_id
                     AND d.branch = de.branch
                     AND d.component_id = de.component_id
                    WHERE d.repo_id = ? AND d.branch = ?
                      AND d.path IN ({placeholders})
                    """,
                    params,
                )
            )

        for component_chunk in _chunks(tuple(old_components)):
            placeholders = ",".join("?" for _ in component_chunk)
            scope_params = (scope.repo, scope.branch, *component_chunk)
            connection.execute(
                f"DELETE FROM relations WHERE repo_id = ? AND branch = ? "
                f"AND caller_id IN ({placeholders})",
                scope_params,
            )
            connection.execute(
                f"DELETE FROM relations WHERE repo_id = ? AND branch = ? "
                f"AND callee_id IN ({placeholders})",
                scope_params,
            )
            connection.execute(
                f"DELETE FROM symbol_calls WHERE repo_id = ? AND branch = ? "
                f"AND caller_id IN ({placeholders})",
                scope_params,
            )
            connection.execute(
                f"DELETE FROM embedding_buckets WHERE repo_id = ? AND branch = ? "
                f"AND component_id IN ({placeholders})",
                scope_params,
            )
            connection.execute(
                f"DELETE FROM document_embeddings WHERE repo_id = ? AND branch = ? "
                f"AND component_id IN ({placeholders})",
                scope_params,
            )

        for chunk in _chunks(paths):
            placeholders = ",".join("?" for _ in chunk)
            params = (scope.repo, scope.branch, *chunk)
            for table in ("documents", "symbols", "files"):
                connection.execute(
                    f"DELETE FROM {table} WHERE repo_id = ? AND branch = ? "
                    f"AND path IN ({placeholders})",
                    params,
                )
        return old_components, old_names, old_artifacts, old_embeddings

    @staticmethod
    def _delete_orphan_candidates(
        connection: sqlite3.Connection,
        *,
        artifact_ids: set[str],
        embedding_keys: set[tuple[str, str]],
    ) -> None:
        for artifact_chunk in _chunks(tuple(artifact_ids)):
            placeholders = ",".join("?" for _ in artifact_chunk)
            connection.execute(
                f"""
                DELETE FROM parse_artifacts
                WHERE artifact_id IN ({placeholders})
                  AND NOT EXISTS (
                    SELECT 1 FROM files
                    WHERE files.artifact_id = parse_artifacts.artifact_id
                  )
                """,
                artifact_chunk,
            )
        for content_signature, model in embedding_keys:
            connection.execute(
                """
                DELETE FROM embeddings
                WHERE content_signature = ? AND model = ?
                  AND NOT EXISTS (
                    SELECT 1 FROM document_embeddings AS de
                    WHERE de.content_signature = embeddings.content_signature
                      AND de.model = embeddings.model
                  )
                """,
                (content_signature, model),
            )

    def _insert_entries(
        self,
        connection: sqlite3.Connection,
        scope: IndexScope,
        entries: tuple[TreeEntry, ...],
        prepared: _PreparedArtifacts,
    ) -> tuple[set[str], set[str]]:
        components: set[str] = set()
        names: set[str] = set()
        for entry in entries:
            artifact_id = prepared.entry_artifacts[entry.path]
            connection.execute(
                """
                INSERT INTO files(repo_id, branch, path, blob_id, artifact_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (scope.repo, scope.branch, entry.path, entry.blob_id, artifact_id),
            )
            records = json.loads(prepared.payloads[artifact_id])
            for record in records:
                local_id = str(record["local_id"])
                component_id = f"{entry.path}::{local_id}"
                symbol = local_id
                short_name = local_id.rsplit(".", 1)[-1]
                components.add(component_id)
                names.add(short_name)
                imports = [str(value) for value in record.get("imports", [])]
                calls = sorted({str(value) for value in record.get("calls", []) if value})
                docstring = str(record.get("docstring") or "")
                source = str(record.get("source") or "")
                kind = str(record.get("type") or "symbol")
                path_key = _key(entry.path)
                connection.execute(
                    """
                    INSERT INTO symbols(
                        repo_id, branch, component_id, component_key,
                        path, path_key, local_id, symbol, symbol_key,
                        short_name, short_key, kind, line_start, line_end,
                        docstring, source, imports_json,
                        entry_point_kind, entry_point_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scope.repo,
                        scope.branch,
                        component_id,
                        _key(component_id),
                        entry.path,
                        path_key,
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
                    INSERT INTO symbol_calls(repo_id, branch, caller_id, call_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    [(scope.repo, scope.branch, component_id, call) for call in calls],
                )
                text = "\n".join(part for part in (
                    component_id,
                    entry.path,
                    symbol,
                    docstring,
                    source,
                    " ".join(calls),
                    " ".join(imports),
                ) if part)
                connection.execute(
                    """
                    INSERT INTO documents(
                        repo_id, branch, component_id, path, symbol, kind,
                        text, content_signature
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scope.repo,
                        scope.branch,
                        component_id,
                        entry.path,
                        symbol,
                        kind,
                        text,
                        hashlib.sha256(text.encode()).hexdigest(),
                    ),
                )
        return components, names

    def _rebuild_relations(
        self,
        connection: sqlite3.Connection,
        scope: IndexScope,
        *,
        affected_names: set[str],
        changed_components: set[str],
        removed_components: set[str],
    ) -> int:
        affected_callers = set(changed_components)
        for chunk in _chunks(tuple(affected_names)):
            placeholders = ",".join("?" for _ in chunk)
            rows = connection.execute(
                f"""
                SELECT caller_id FROM symbol_calls
                WHERE repo_id = ? AND branch = ? AND call_name IN ({placeholders})
                """,
                (scope.repo, scope.branch, *chunk),
            )
            affected_callers.update(row["caller_id"] for row in rows)

        for chunk in _chunks(tuple(affected_callers)):
            placeholders = ",".join("?" for _ in chunk)
            connection.execute(
                f"DELETE FROM relations WHERE repo_id = ? AND branch = ? "
                f"AND caller_id IN ({placeholders})",
                (scope.repo, scope.branch, *chunk),
            )
        for chunk in _chunks(tuple(removed_components)):
            placeholders = ",".join("?" for _ in chunk)
            connection.execute(
                f"DELETE FROM relations WHERE repo_id = ? AND branch = ? "
                f"AND callee_id IN ({placeholders})",
                (scope.repo, scope.branch, *chunk),
            )

        inserted = 0
        for caller_id in sorted(affected_callers):
            caller = connection.execute(
                """
                SELECT path FROM symbols
                WHERE repo_id = ? AND branch = ? AND component_id = ?
                """,
                (scope.repo, scope.branch, caller_id),
            ).fetchone()
            if not caller:
                continue
            calls = connection.execute(
                """
                SELECT call_name FROM symbol_calls
                WHERE repo_id = ? AND branch = ? AND caller_id = ?
                ORDER BY call_name
                """,
                (scope.repo, scope.branch, caller_id),
            )
            for call in calls:
                targets = list(connection.execute(
                    """
                    SELECT component_id, path FROM symbols
                    WHERE repo_id = ? AND branch = ? AND short_key = ?
                    ORDER BY component_id
                    """,
                    (scope.repo, scope.branch, _key(call["call_name"])),
                ))
                same_file = [target for target in targets if target["path"] == caller["path"]]
                for target in same_file or targets:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO relations(
                            repo_id, branch, caller_id, callee_id, kind
                        ) VALUES (?, ?, ?, ?, 'call')
                        """,
                        (scope.repo, scope.branch, caller_id, target["component_id"]),
                    )
                    inserted += 1
        return inserted

    def _exact_candidates(
        self,
        connection: sqlite3.Connection,
        scope: IndexScope,
        query: str,
        limit: int,
    ) -> list[dict]:
        query_key = _key(query)
        rows = connection.execute(
            """
            SELECT
                s.component_id, s.path, s.symbol, s.kind,
                s.line_start, s.line_end, s.source,
                CASE
                    WHEN s.component_key = ? THEN 100.0
                    WHEN s.symbol_key = ? THEN 90.0
                    WHEN s.short_key = ? THEN 85.0
                    WHEN s.path_key = ? THEN 80.0
                    ELSE 0.0
                END AS exact_score
            FROM symbols AS s
            WHERE s.repo_id = ? AND s.branch = ?
              AND (
                  s.component_key = ? OR s.symbol_key = ? OR
                  s.short_key = ? OR s.path_key = ?
              )
            ORDER BY exact_score DESC, s.component_id
            LIMIT ?
            """,
            (
                query_key,
                query_key,
                query_key,
                query_key,
                scope.repo,
                scope.branch,
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
        scope: IndexScope,
        query: str,
        limit: int,
    ) -> list[dict]:
        expression = _fts_expression(query)
        if not expression:
            return []
        try:
            rows = connection.execute(
                """
                SELECT
                    s.component_id, s.path, s.symbol, s.kind,
                    s.line_start, s.line_end, s.source,
                    bm25(documents_fts, 2.0, 5.0, 1.0) AS lexical_rank
                FROM documents_fts
                JOIN documents AS d ON d.id = documents_fts.rowid
                JOIN symbols AS s
                  ON s.repo_id = d.repo_id
                 AND s.branch = d.branch
                 AND s.component_id = d.component_id
                WHERE documents_fts MATCH ?
                  AND d.repo_id = ? AND d.branch = ?
                ORDER BY lexical_rank, s.component_id
                LIMIT ?
                """,
                (expression, scope.repo, scope.branch, limit),
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
                    target=_target(scope),
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
        scope: IndexScope,
        matches: tuple[SearchHit, ...],
        limit: int,
    ) -> tuple[SearchHit, ...]:
        if not matches or limit == 0:
            return ()
        direct = {hit.component_id for hit in matches}
        related_scores: dict[str, float] = {}
        for rank, hit in enumerate(matches, start=1):
            rows = connection.execute(
                """
                SELECT caller_id, callee_id
                FROM relations
                WHERE repo_id = ? AND branch = ?
                  AND (caller_id = ? OR callee_id = ?)
                ORDER BY caller_id, callee_id
                """,
                (scope.repo, scope.branch, hit.component_id, hit.component_id),
            )
            for row in rows:
                neighbor = (
                    row["callee_id"]
                    if row["caller_id"] == hit.component_id
                    else row["caller_id"]
                )
                if neighbor in direct:
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
                f"""
                SELECT component_id, path, symbol, kind, line_start, line_end, source
                FROM symbols
                WHERE repo_id = ? AND branch = ?
                  AND component_id IN ({placeholders})
                """,
                (scope.repo, scope.branch, *chunk),
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
            SELECT g.id, g.generation, g.tree_id
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


def _count(connection: sqlite3.Connection, table: str, scope: IndexScope) -> int:
    row = connection.execute(
        f"SELECT COUNT(*) FROM {table} WHERE repo_id = ? AND branch = ?",
        (scope.repo, scope.branch),
    ).fetchone()
    return int(row[0])


def _chunks(values: Sequence[object], size: int = 400) -> Iterable[tuple[object, ...]]:
    for start in range(0, len(values), size):
        yield tuple(values[start:start + size])


def _head_identity(head: _Head | None) -> tuple[int, str] | None:
    return None if head is None else (head.generation_id, head.tree_id)


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
