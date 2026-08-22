from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA_VERSION = 4
MAX_COMPACT_PAGES = 4096


class RepositoryStoreError(RuntimeError):
    pass


class RepositoryStoreVersionError(RepositoryStoreError):
    pass


class RepositoryStore:
    """SQLite connection and schema lifecycle for RepositoryIndex."""

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    @contextmanager
    def transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def compact(self) -> int:
        """Return the number of freelist pages reclaimed from this index."""
        connection = self.connect()
        try:
            before = int(connection.execute("PRAGMA freelist_count").fetchone()[0])
            after = before
            for _ in range(min(before, MAX_COMPACT_PAGES)):
                connection.execute("PRAGMA incremental_vacuum(1)")
                current = int(connection.execute(
                    "PRAGMA freelist_count"
                ).fetchone()[0])
                if current >= after:
                    break
                after = current
            return max(0, before - after)
        finally:
            connection.close()

    def _initialize(self) -> None:
        connection = self.connect()
        try:
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version > SCHEMA_VERSION:
                raise RepositoryStoreVersionError(
                    f"repository index schema v{version} is newer than supported "
                    f"v{SCHEMA_VERSION}"
                )
            # SQLite may reject a concurrent journal-mode negotiation without
            # invoking the configured busy handler. Retry only that transient
            # lock boundary; the remaining schema statements are idempotent.
            deadline = time.monotonic() + 30
            while True:
                try:
                    connection.execute("PRAGMA journal_mode = WAL")
                    break
                except sqlite3.OperationalError as error:
                    if "locked" not in str(error).lower() or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("BEGIN EXCLUSIVE")
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version > SCHEMA_VERSION:
                raise RepositoryStoreVersionError(
                    f"repository index schema v{version} is newer than supported "
                    f"v{SCHEMA_VERSION}"
                )
            rebuilt = 0 < version < SCHEMA_VERSION
            if rebuilt:
                # Repository indexes are derived entirely from Git. Rebuilding is
                # safer and simpler than migrating materialized search state.
                _execute_statements(connection, _DROP_SCHEMA)
            if version < SCHEMA_VERSION:
                _execute_statements(connection, _SCHEMA)
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            connection.commit()
            connection.execute("PRAGMA foreign_keys = ON")

            connection.execute("PRAGMA auto_vacuum = INCREMENTAL")
            needs_vacuum = (
                rebuilt
                or int(connection.execute("PRAGMA auto_vacuum").fetchone()[0]) != 2
            )
            if needs_vacuum:
                # Changing an existing database from NONE to INCREMENTAL is
                # persisted only by a full VACUUM. This is a one-time schema
                # initialization cost; later reclamation stays incremental.
                connection.execute("VACUUM")
        except RepositoryStoreVersionError:
            if connection.in_transaction:
                connection.rollback()
            raise
        except sqlite3.Error as error:
            if connection.in_transaction:
                connection.rollback()
            raise RepositoryStoreError(str(error)) from error
        finally:
            connection.close()


def _execute_statements(connection: sqlite3.Connection, script: str) -> None:
    statement = ""
    for line in script.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            connection.execute(statement)
            statement = ""
    if statement.strip():
        raise RepositoryStoreError("incomplete repository schema statement")


_DROP_SCHEMA = """
DROP TABLE IF EXISTS documents_fts;
DROP TABLE IF EXISTS artifact_documents_fts;
DROP TABLE IF EXISTS embedding_buckets;
DROP TABLE IF EXISTS document_embeddings;
DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS enrichment_heads;
DROP TABLE IF EXISTS enrichment_jobs;
DROP TABLE IF EXISTS enrichment_revisions;
DROP TABLE IF EXISTS relations;
DROP TABLE IF EXISTS snapshot_relations;
DROP TABLE IF EXISTS relation_cache_states;
DROP TABLE IF EXISTS symbol_calls;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS symbols;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS snapshot_changes;
DROP TABLE IF EXISTS artifact_documents;
DROP TABLE IF EXISTS artifact_calls;
DROP TABLE IF EXISTS artifact_symbols;
DROP TABLE IF EXISTS generation_changes;
DROP TABLE IF EXISTS branch_heads;
DROP TABLE IF EXISTS generations;
DROP TABLE IF EXISTS snapshots;
DROP TABLE IF EXISTS parse_artifacts;
DROP TABLE IF EXISTS repositories;
"""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS repositories (
    repo_id TEXT PRIMARY KEY,
    source_root TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parse_artifacts (
    artifact_id TEXT PRIMARY KEY,
    blob_id TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    context_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(blob_id, parser_version, context_hash)
);

CREATE TABLE IF NOT EXISTS artifact_symbols (
    artifact_id TEXT NOT NULL,
    local_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    symbol_key TEXT NOT NULL,
    short_name TEXT NOT NULL,
    short_key TEXT NOT NULL,
    kind TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    docstring TEXT NOT NULL,
    source TEXT NOT NULL,
    imports_json TEXT NOT NULL,
    entry_point_kind TEXT NOT NULL,
    entry_point_path TEXT NOT NULL,
    PRIMARY KEY(artifact_id, local_id),
    FOREIGN KEY(artifact_id) REFERENCES parse_artifacts(artifact_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS artifact_symbols_name_idx
ON artifact_symbols(short_key, symbol_key);

CREATE TABLE IF NOT EXISTS artifact_calls (
    artifact_id TEXT NOT NULL,
    local_id TEXT NOT NULL,
    call_name TEXT NOT NULL,
    call_key TEXT NOT NULL,
    PRIMARY KEY(artifact_id, local_id, call_name),
    FOREIGN KEY(artifact_id, local_id)
        REFERENCES artifact_symbols(artifact_id, local_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS artifact_calls_name_idx
ON artifact_calls(call_key);

CREATE TABLE IF NOT EXISTS artifact_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id TEXT NOT NULL,
    local_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL,
    content_signature TEXT NOT NULL,
    UNIQUE(artifact_id, local_id),
    FOREIGN KEY(artifact_id, local_id)
        REFERENCES artifact_symbols(artifact_id, local_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS artifact_documents_signature_idx
ON artifact_documents(content_signature);

CREATE VIRTUAL TABLE IF NOT EXISTS artifact_documents_fts USING fts5(
    symbol,
    text,
    content='artifact_documents',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS artifact_documents_ai
AFTER INSERT ON artifact_documents BEGIN
    INSERT INTO artifact_documents_fts(rowid, symbol, text)
    VALUES (new.id, new.symbol, new.text);
END;

CREATE TRIGGER IF NOT EXISTS artifact_documents_ad
AFTER DELETE ON artifact_documents BEGIN
    INSERT INTO artifact_documents_fts(
        artifact_documents_fts, rowid, symbol, text
    ) VALUES ('delete', old.id, old.symbol, old.text);
END;

CREATE TRIGGER IF NOT EXISTS artifact_documents_au
AFTER UPDATE ON artifact_documents BEGIN
    INSERT INTO artifact_documents_fts(
        artifact_documents_fts, rowid, symbol, text
    ) VALUES ('delete', old.id, old.symbol, old.text);
    INSERT INTO artifact_documents_fts(rowid, symbol, text)
    VALUES (new.id, new.symbol, new.text);
END;

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    tree_id TEXT NOT NULL,
    base_snapshot_id INTEGER,
    depth INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(repo_id, tree_id),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id) ON DELETE CASCADE,
    FOREIGN KEY(base_snapshot_id) REFERENCES snapshots(id)
);

CREATE INDEX IF NOT EXISTS snapshots_base_idx
ON snapshots(base_snapshot_id);

CREATE TABLE IF NOT EXISTS snapshot_changes (
    snapshot_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    path_key TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('upsert', 'delete')),
    blob_id TEXT,
    artifact_id TEXT,
    PRIMARY KEY(snapshot_id, path),
    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE,
    FOREIGN KEY(artifact_id) REFERENCES parse_artifacts(artifact_id)
);

CREATE INDEX IF NOT EXISTS snapshot_changes_artifact_idx
ON snapshot_changes(snapshot_id, artifact_id);

CREATE INDEX IF NOT EXISTS snapshot_changes_artifact_lookup_idx
ON snapshot_changes(artifact_id) WHERE artifact_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation INTEGER NOT NULL,
    tree_id TEXT NOT NULL,
    snapshot_id INTEGER NOT NULL,
    parent_id INTEGER,
    created_at TEXT NOT NULL,
    changed_count INTEGER NOT NULL,
    removed_count INTEGER NOT NULL,
    parsed_count INTEGER NOT NULL,
    reused_count INTEGER NOT NULL,
    UNIQUE(repo_id, branch, generation),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id) ON DELETE CASCADE,
    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id),
    FOREIGN KEY(parent_id) REFERENCES generations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS branch_heads (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation_id INTEGER NOT NULL,
    PRIMARY KEY(repo_id, branch),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id) ON DELETE CASCADE,
    FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS generation_changes (
    generation_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('upsert', 'delete')),
    blob_id TEXT,
    PRIMARY KEY(generation_id, path),
    FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relation_cache_states (
    snapshot_id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS snapshot_relations (
    snapshot_id INTEGER NOT NULL,
    caller_id TEXT NOT NULL,
    callee_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    PRIMARY KEY(snapshot_id, caller_id, callee_id, kind),
    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS snapshot_relations_callee_idx
ON snapshot_relations(snapshot_id, callee_id, kind);

CREATE TABLE IF NOT EXISTS embeddings (
    content_signature TEXT NOT NULL,
    model TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector BLOB NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(content_signature, model)
);

CREATE TABLE IF NOT EXISTS embedding_buckets (
    content_signature TEXT NOT NULL,
    model TEXT NOT NULL,
    table_no INTEGER NOT NULL,
    bucket INTEGER NOT NULL,
    PRIMARY KEY(content_signature, model, table_no),
    FOREIGN KEY(content_signature, model)
        REFERENCES embeddings(content_signature, model)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS embedding_buckets_lookup_idx
ON embedding_buckets(model, table_no, bucket);

CREATE TABLE IF NOT EXISTS enrichment_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation_id INTEGER NOT NULL,
    revision INTEGER NOT NULL,
    model TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    coverage REAL NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(repo_id, branch, revision),
    UNIQUE(generation_id, model),
    FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enrichment_heads (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    revision_id INTEGER NOT NULL,
    PRIMARY KEY(repo_id, branch),
    FOREIGN KEY(revision_id) REFERENCES enrichment_revisions(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enrichment_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN (
        'pending', 'running', 'completed', 'failed', 'superseded'
    )),
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT NOT NULL DEFAULT '',
    owner_token TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(generation_id),
    FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS enrichment_jobs_status_idx
ON enrichment_jobs(status, updated_at);
"""


__all__ = [
    "RepositoryStore",
    "RepositoryStoreError",
    "RepositoryStoreVersionError",
    "SCHEMA_VERSION",
]
