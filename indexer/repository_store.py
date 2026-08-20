from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA_VERSION = 2


class RepositoryStoreError(RuntimeError):
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

    def _initialize(self) -> None:
        connection = self.connect()
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version not in {0, SCHEMA_VERSION}:
                raise RepositoryStoreError(
                    f"unsupported repository index schema {version}; expected {SCHEMA_VERSION}"
                )
            connection.executescript(_SCHEMA)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        except sqlite3.Error as error:
            raise RepositoryStoreError(str(error)) from error
        finally:
            connection.close()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS repositories (
    repo_id TEXT PRIMARY KEY,
    source_root TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation INTEGER NOT NULL,
    tree_id TEXT NOT NULL,
    parent_id INTEGER,
    created_at TEXT NOT NULL,
    changed_count INTEGER NOT NULL,
    removed_count INTEGER NOT NULL,
    parsed_count INTEGER NOT NULL,
    reused_count INTEGER NOT NULL,
    UNIQUE(repo_id, branch, generation),
    UNIQUE(repo_id, branch, tree_id),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id),
    FOREIGN KEY(parent_id) REFERENCES generations(id)
);

CREATE TABLE IF NOT EXISTS branch_heads (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation_id INTEGER NOT NULL,
    PRIMARY KEY(repo_id, branch),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id),
    FOREIGN KEY(generation_id) REFERENCES generations(id)
);

CREATE TABLE IF NOT EXISTS generation_changes (
    generation_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('upsert', 'delete')),
    blob_id TEXT,
    PRIMARY KEY(generation_id, path),
    FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
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

CREATE TABLE IF NOT EXISTS files (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    path TEXT NOT NULL,
    blob_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    PRIMARY KEY(repo_id, branch, path),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id),
    FOREIGN KEY(artifact_id) REFERENCES parse_artifacts(artifact_id)
);

CREATE INDEX IF NOT EXISTS files_blob_idx
ON files(blob_id, artifact_id);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    component_id TEXT NOT NULL,
    component_key TEXT NOT NULL,
    path TEXT NOT NULL,
    path_key TEXT NOT NULL,
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
    UNIQUE(repo_id, branch, component_id),
    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id)
);

CREATE INDEX IF NOT EXISTS symbols_path_idx
ON symbols(repo_id, branch, path);

CREATE INDEX IF NOT EXISTS symbols_name_idx
ON symbols(repo_id, branch, short_key, symbol_key);

CREATE INDEX IF NOT EXISTS symbols_component_idx
ON symbols(repo_id, branch, component_key);

CREATE INDEX IF NOT EXISTS symbols_path_key_idx
ON symbols(repo_id, branch, path_key);

CREATE TABLE IF NOT EXISTS symbol_calls (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    caller_id TEXT NOT NULL,
    call_name TEXT NOT NULL,
    PRIMARY KEY(repo_id, branch, caller_id, call_name)
);

CREATE INDEX IF NOT EXISTS symbol_calls_name_idx
ON symbol_calls(repo_id, branch, call_name);

CREATE TABLE IF NOT EXISTS relations (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    caller_id TEXT NOT NULL,
    callee_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    PRIMARY KEY(repo_id, branch, caller_id, callee_id, kind)
);

CREATE INDEX IF NOT EXISTS relations_callee_idx
ON relations(repo_id, branch, callee_id, kind);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    component_id TEXT NOT NULL,
    path TEXT NOT NULL,
    symbol TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL,
    content_signature TEXT NOT NULL,
    UNIQUE(repo_id, branch, component_id)
);

CREATE INDEX IF NOT EXISTS documents_scope_idx
ON documents(repo_id, branch, component_id);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    path,
    symbol,
    text,
    content='documents',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid, path, symbol, text)
    VALUES (new.id, new.path, new.symbol, new.text);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, path, symbol, text)
    VALUES ('delete', old.id, old.path, old.symbol, old.text);
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, path, symbol, text)
    VALUES ('delete', old.id, old.path, old.symbol, old.text);
    INSERT INTO documents_fts(rowid, path, symbol, text)
    VALUES (new.id, new.path, new.symbol, new.text);
END;

CREATE TABLE IF NOT EXISTS embeddings (
    content_signature TEXT NOT NULL,
    model TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector BLOB NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(content_signature, model)
);

CREATE TABLE IF NOT EXISTS document_embeddings (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    component_id TEXT NOT NULL,
    content_signature TEXT NOT NULL,
    model TEXT NOT NULL,
    PRIMARY KEY(repo_id, branch, component_id),
    FOREIGN KEY(content_signature, model)
        REFERENCES embeddings(content_signature, model)
);

CREATE INDEX IF NOT EXISTS document_embeddings_signature_idx
ON document_embeddings(content_signature, model);

CREATE TABLE IF NOT EXISTS embedding_buckets (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    component_id TEXT NOT NULL,
    model TEXT NOT NULL,
    table_no INTEGER NOT NULL,
    bucket INTEGER NOT NULL,
    PRIMARY KEY(repo_id, branch, component_id, model, table_no)
);

CREATE INDEX IF NOT EXISTS embedding_buckets_lookup_idx
ON embedding_buckets(repo_id, branch, model, table_no, bucket);

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
    FOREIGN KEY(generation_id) REFERENCES generations(id)
);

CREATE TABLE IF NOT EXISTS enrichment_heads (
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    revision_id INTEGER NOT NULL,
    PRIMARY KEY(repo_id, branch),
    FOREIGN KEY(revision_id) REFERENCES enrichment_revisions(id)
);

CREATE TABLE IF NOT EXISTS enrichment_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,
    branch TEXT NOT NULL,
    generation_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'running', 'completed', 'failed', 'superseded')),
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(generation_id),
    FOREIGN KEY(generation_id) REFERENCES generations(id)
);

CREATE INDEX IF NOT EXISTS enrichment_jobs_status_idx
ON enrichment_jobs(status, updated_at);
"""


__all__ = ["RepositoryStore", "RepositoryStoreError", "SCHEMA_VERSION"]
