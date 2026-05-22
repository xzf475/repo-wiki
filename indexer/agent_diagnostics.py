from __future__ import annotations

from pathlib import Path

from indexer.config import Config
import indexer.retrieval as _retrieval

def diagnose_index(repo_root: Path, cfg: Config) -> dict:
    from indexer.manifest import load_manifest
    from indexer.wiki import resolve_wiki_page_path

    manifest_path = repo_root / ".indexer" / "manifest.json"
    manifest = load_manifest(repo_root)
    wiki_index = repo_root / cfg.wiki_dir / "INDEX.md"
    skill_file = repo_root / ".indexer" / "skills" / "codebase.md"
    vector_dir = repo_root / cfg.vector_store.persist_dir

    missing_sources = sorted([path for path in manifest.files if not (repo_root / path).exists()])
    missing_wiki_pages = []
    wiki_dir = repo_root / cfg.wiki_dir
    for entry in manifest.files.values():
        if entry.component_ids and not resolve_wiki_page_path(entry.wiki_page, wiki_dir):
            missing_wiki_pages.append(entry.wiki_page)
    missing_wiki_pages = sorted(set(missing_wiki_pages))

    index_status = _retrieval.get_index_status(repo_root)
    manifest_file_count = len(manifest.files)
    missing_source_count = len(missing_sources)
    missing_wiki_count = len(missing_wiki_pages)
    source_ok_count = max(0, manifest_file_count - missing_source_count)
    wiki_ok_count = max(0, manifest_file_count - missing_wiki_count)
    manifest_to_source_ratio = round(source_ok_count / manifest_file_count, 4) if manifest_file_count else 1.0
    manifest_to_wiki_ratio = round(wiki_ok_count / manifest_file_count, 4) if manifest_file_count else 1.0
    stale_file_count = int(index_status.get("stale_file_count", 0) or 0)
    removed_file_count = int(index_status.get("removed_file_count", 0) or 0)
    checks = {
        "manifest": {"ok": manifest_path.exists(), "path": str(manifest_path), "indexed_files": len(manifest.files)},
        "wiki_index": {"ok": wiki_index.exists(), "path": str(wiki_index)},
        "skill_file": {"ok": skill_file.exists(), "path": str(skill_file)},
        "vector_db": {"ok": vector_dir.exists(), "path": str(vector_dir)},
        "source_files": {"ok": not missing_sources, "missing": missing_sources[:50], "missing_count": len(missing_sources)},
        "wiki_pages": {"ok": not missing_wiki_pages, "missing": missing_wiki_pages[:50], "missing_count": len(missing_wiki_pages)},
        "freshness": {"ok": not index_status.get("is_stale"), "status": index_status},
        "consistency": {
            "ok": not missing_sources and not missing_wiki_pages and not stale_file_count and not removed_file_count,
            "manifest_to_source_ratio": manifest_to_source_ratio,
            "manifest_to_wiki_ratio": manifest_to_wiki_ratio,
            "stale_file_count": stale_file_count,
            "removed_file_count": removed_file_count,
            "orphan_vector_ids": [],
            "orphan_vector_count": 0,
        },
    }
    healthy = all(item.get("ok", False) for item in checks.values())
    return {
        "healthy": healthy,
        "summary": {
            "manifest_file_count": manifest_file_count,
            "missing_source_count": missing_source_count,
            "missing_wiki_page_count": missing_wiki_count,
            "stale_file_count": stale_file_count,
            "removed_file_count": removed_file_count,
            "vector_present": vector_dir.exists(),
            "wiki_index_present": wiki_index.exists(),
            "skill_file_present": skill_file.exists(),
        },
        "checks": checks,
    }

__all__ = ['diagnose_index']
