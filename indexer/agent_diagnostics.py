from __future__ import annotations

from pathlib import Path

from indexer.config import Config
from indexer.repository_service import RepositoryService, default_branch
import indexer.retrieval as _retrieval

def diagnose_index(repo_root: Path, cfg: Config) -> dict:
    service = RepositoryService(
        repo_root.name,
        repo_root,
        default_branch(repo_root),
        config=cfg,
    )
    database_path = repo_root / ".indexer" / "state" / "repository-index.sqlite3"
    wiki_index = repo_root / cfg.wiki_dir / "INDEX.md"
    skill_file = repo_root / ".indexer" / "skills" / "codebase.md"
    index_status = _retrieval.get_index_status(repo_root)
    indexed_files = service.index.files(service.scope)
    missing_sources = sorted(
        path for path in indexed_files
        if not (repo_root / path).exists()
    )
    generated_pages = list((repo_root / cfg.wiki_dir).glob("*.md"))
    missing_wiki_pages = [] if generated_pages else ["INDEX.md"]
    indexed_file_count = len(indexed_files)
    missing_source_count = len(missing_sources)
    missing_wiki_count = len(missing_wiki_pages)
    source_ok_count = max(0, indexed_file_count - missing_source_count)
    index_to_source_ratio = round(source_ok_count / indexed_file_count, 4) if indexed_file_count else 1.0
    stale_file_count = int(index_status.get("stale_file_count", 0) or 0)
    removed_file_count = int(index_status.get("removed_file_count", 0) or 0)
    checks = {
        "repository_index": {
            "ok": database_path.exists() and index_status.get("generation") is not None,
            "path": str(database_path),
            "generation": index_status.get("generation"),
            "indexed_files": indexed_file_count,
        },
        "wiki_index": {"ok": wiki_index.exists(), "path": str(wiki_index)},
        "skill_file": {"ok": skill_file.exists(), "path": str(skill_file)},
        "dense_enrichment": {
            "ok": True,
            "state": index_status.get("dense_state", "not_ready"),
            "revision": index_status.get("enrichment_revision"),
        },
        "source_files": {"ok": not missing_sources, "missing": missing_sources[:50], "missing_count": len(missing_sources)},
        "wiki_pages": {"ok": not missing_wiki_pages, "missing": missing_wiki_pages[:50], "missing_count": len(missing_wiki_pages)},
        "freshness": {"ok": not index_status.get("is_stale"), "status": index_status},
        "consistency": {
            "ok": not missing_sources and not missing_wiki_pages and not stale_file_count and not removed_file_count,
            "index_to_source_ratio": index_to_source_ratio,
            "stale_file_count": stale_file_count,
            "removed_file_count": removed_file_count,
        },
    }
    healthy = all(item.get("ok", False) for item in checks.values())
    return {
        "healthy": healthy,
        "summary": {
            "indexed_file_count": indexed_file_count,
            "missing_source_count": missing_source_count,
            "missing_wiki_page_count": missing_wiki_count,
            "stale_file_count": stale_file_count,
            "removed_file_count": removed_file_count,
            "dense_state": index_status.get("dense_state", "not_ready"),
            "wiki_index_present": wiki_index.exists(),
            "skill_file_present": skill_file.exists(),
        },
        "checks": checks,
    }

__all__ = ['diagnose_index']
