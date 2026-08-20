from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from indexer.config import Config, load_config
from indexer.git import current_branch
from indexer.git_snapshot import GitSnapshot, GitSnapshotError, WORKTREE_REVISION
from indexer.repository_embedding import ConfiguredEmbeddingProvider
from indexer.repository_index import (
    EnrichmentReport,
    IndexScope,
    RepositoryIndex,
    RepositoryIndexError,
    SearchHit,
    SearchRequest,
    SymbolRecord,
    SyncReport,
    SyncRequest,
)


class RepositoryService:
    """Application seam shared by CLI, REST, and MCP adapters."""

    def __init__(
        self,
        repo: str,
        root: Path,
        branch: str,
        *,
        config: Config | None = None,
    ):
        self.repo = repo
        self.root = root.resolve()
        self.branch = branch
        self.config = config or load_config(self.root)
        self.scope = IndexScope(repo, branch)
        self.index = RepositoryIndex.open(
            self.root,
            embedding_provider=ConfiguredEmbeddingProvider(self.config.embedding),
        )

    def sync(
        self,
        *,
        revision: str | None = None,
        enrich: bool = False,
        enrichment_required: bool = False,
    ) -> dict:
        resolved_revision = revision or resolve_revision(self.root, self.branch)
        report = self.index.sync(SyncRequest(
            repo=self.repo,
            root=self.root,
            branch=self.branch,
            revision=resolved_revision,
        ))
        enrichment: EnrichmentReport | None = None
        degradation = ""
        if enrich:
            try:
                enrichment = self.index.enrich(self.scope)
            except RepositoryIndexError as error:
                if enrichment_required:
                    raise
                degradation = f"{error.code}:{error}"
        return {
            "sync": asdict(report),
            "enrichment": asdict(enrichment) if enrichment else None,
            "degradation": degradation or None,
        }

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        related_limit: int | None = None,
        retrieval: str = "preferred",
    ) -> dict:
        result = self.index.search(SearchRequest(
            scope=self.scope,
            query=query,
            limit=limit,
            related_limit=related_limit,
            retrieval=retrieval,
        ))
        matches = [_hit_dict(hit, self.branch) for hit in result.matches]
        related = [_hit_dict(hit, self.branch, relation="call") for hit in result.related]
        return {
            "results": matches,
            "matches": matches,
            "related": related,
            "total": len(matches),
            "generation": result.generation,
            "tree_id": result.tree_id,
            "retrieval": result.retrieval,
            "degradations": list(result.degradations),
            "search_metrics": {
                "generation": result.generation,
                "retrieval": result.retrieval,
                "degradations": list(result.degradations),
                "timings_ms": {"total": result.elapsed_ms},
                "candidate_counts": {
                    "matches": len(matches),
                    "related": len(related),
                },
            },
        }

    def lookup(self, component_ids: list[str] | tuple[str, ...]) -> list[dict]:
        return [
            _record_dict(record, self.branch)
            for record in self.index.symbols(
                self.scope,
                component_ids=tuple(component_ids),
            )
        ]

    def trace(
        self,
        component_id: str,
        *,
        direction: str = "down",
        max_depth: int = 3,
    ) -> list[dict]:
        return [
            _record_dict(record, self.branch)
            for record in self.index.trace(
                self.scope,
                component_id,
                direction=direction,
                max_depth=max_depth,
            )
        ]

    def project(self) -> dict:
        from indexer.repository_projection import write_repository_projection

        return asdict(write_repository_projection(
            self.root,
            self.config,
            self.index,
            self.scope,
        ))

    def inspect(self, *, revision: str | None = None) -> dict:
        status = self.index.inspect(self.scope)
        snapshot = GitSnapshot(self.root)
        current_tree = ""
        stale_files: list[str] = []
        removed_files: list[str] = []
        reasons: list[str] = []
        try:
            resolved_revision = revision or resolve_revision(self.root, self.branch)
            current_tree = snapshot.resolve_tree(resolved_revision)
            if not status.exists:
                reasons.append("missing generation")
                initial = snapshot.initial_delta(current_tree)
                stale_files = [entry.path for entry in initial.changed]
            elif current_tree != status.tree_id:
                delta = snapshot.delta(status.tree_id, current_tree)
                stale_files = [entry.path for entry in delta.changed]
                removed_files = list(delta.removed)
                if stale_files or removed_files:
                    reasons.append("source tree changed")
        except GitSnapshotError as error:
            reasons.append(f"source unavailable: {error}")

        return {
            "is_stale": bool(reasons),
            "reasons": reasons,
            "repo": self.repo,
            "current_branch": self.branch,
            "generation": status.generation,
            "indexed_tree": status.tree_id or None,
            "current_tree": current_tree or None,
            "indexed_files": status.files,
            "symbols": status.symbols,
            "relations": status.relations,
            "stale_files": stale_files[:50],
            "removed_files": removed_files[:50],
            "stale_file_count": len(stale_files),
            "removed_file_count": len(removed_files),
            "dense_state": status.dense_state,
            "enrichment_revision": status.enrichment_revision,
            "pending_jobs": status.pending_jobs,
        }


def resolve_revision(root: Path, branch: str) -> str:
    if branch == "worktree":
        return WORKTREE_REVISION
    snapshot = GitSnapshot(root)
    candidates = (
        f"refs/remotes/origin/{branch}",
        f"refs/heads/{branch}",
        branch,
    )
    for candidate in dict.fromkeys(candidates):
        try:
            snapshot.resolve_tree(candidate)
            return candidate
        except GitSnapshotError:
            continue
    raise RepositoryIndexError(
        "SOURCE_UNAVAILABLE",
        f"branch {branch!r} was not found",
        phase="capture",
        target=branch,
        retryable=True,
    )


def default_branch(root: Path) -> str:
    return current_branch(root) or "main"


def _hit_dict(hit: SearchHit, branch: str, *, relation: str = "") -> dict:
    reasons = [
        f"{name}={score:.6f}"
        for name, score in hit.score_breakdown.items()
        if score > 0
    ]
    metadata = {
        "branch": branch,
        "file": hit.file,
        "type": hit.type,
        "line_start": hit.line_start,
        "line_end": hit.line_end,
        "score_breakdown": dict(hit.score_breakdown),
    }
    result = {
        "id": hit.component_id,
        "document": hit.source,
        "metadata": metadata,
        "score": hit.score,
        "distance": max(0.0, 1.0 - min(1.0, hit.score)),
        "match_reasons": reasons,
        "score_breakdown": dict(hit.score_breakdown),
    }
    if relation:
        result["relation"] = relation
    return result


def _record_dict(record: SymbolRecord, branch: str) -> dict:
    metadata = {
        "branch": branch,
        "file": record.file,
        "type": record.type,
        "line_start": record.line_start,
        "line_end": record.line_end,
        "docstring": record.docstring,
        "imports": json.dumps(record.imports),
        "calls": json.dumps(record.calls),
        "called_by": json.dumps(record.called_by),
        "entry_point_kind": record.entry_point_kind,
        "entry_point_path": record.entry_point_path,
    }
    return {
        "id": record.component_id,
        "document": record.source,
        "metadata": metadata,
        "score": 1.0,
        "distance": 0.0,
    }


__all__ = ["RepositoryService", "default_branch", "resolve_revision"]
