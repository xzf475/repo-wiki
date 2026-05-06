from __future__ import annotations
import json
import hashlib
import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

MANIFEST_PATH = ".indexer/manifest.json"

@dataclass
class FileEntry:
    hash: str
    wiki_page: str
    component_ids: list[str]

@dataclass
class Manifest:
    last_indexed_commit: str | None
    indexed_at: str
    files: dict[str, FileEntry] = field(default_factory=dict)

    def stale_files(self, repo_root: Path, candidate_paths: list[str]) -> list[str]:
        stale = []
        for rel_path in candidate_paths:
            abs_path = repo_root / rel_path
            if not abs_path.exists():
                continue
            current_hash = compute_hash(abs_path)
            entry = self.files.get(rel_path)
            if current_hash is None or entry is None or entry.hash != current_hash:
                stale.append(rel_path)
        return stale

    def removed_files(self, repo_root: Path, current_tracked: list[str]) -> list[str]:
        tracked_set = set(current_tracked) if current_tracked else None
        removed = []
        for rel_path in list(self.files.keys()):
            abs_path = repo_root / rel_path
            if not abs_path.exists():
                removed.append(rel_path)
            elif tracked_set is not None and rel_path not in tracked_set:
                removed.append(rel_path)
        return removed

def compute_hash(path: Path) -> str | None:
    try:
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        return f"sha256:{h}"
    except OSError:
        logger.warning("Failed to compute hash for %s", path)
        return None

def load_manifest(repo_root: Path) -> Manifest:
    path = repo_root / MANIFEST_PATH
    if not path.exists():
        return Manifest(last_indexed_commit=None, indexed_at="", files={})
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to parse manifest.json: %s", e)
        return Manifest(last_indexed_commit=None, indexed_at="", files={})
    files = {}
    for k, v in data.get("files", {}).items():
        file_hash = v.get("hash", "")
        wiki_page = v.get("wiki_page", "")
        if not file_hash and not wiki_page:
            logger.warning("Skipping manifest entry with missing fields: %s", k)
            continue
        files[k] = FileEntry(
            hash=file_hash,
            wiki_page=wiki_page,
            component_ids=v.get("component_ids", []),
        )
    return Manifest(
        last_indexed_commit=data.get("last_indexed_commit"),
        indexed_at=data.get("indexed_at", ""),
        files=files,
    )

def save_manifest(repo_root: Path, manifest: Manifest) -> None:
    path = repo_root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "last_indexed_commit": manifest.last_indexed_commit,
        "indexed_at": manifest.indexed_at,
        "files": {k: asdict(v) for k, v in manifest.files.items()},
    }
    import tempfile
    with tempfile.NamedTemporaryFile(dir=str(path.parent), suffix=".json.tmp", delete=False, mode="w") as f:
        f.write(json.dumps(data, indent=2))
        tmp_path = f.name
    os.replace(tmp_path, str(path))
