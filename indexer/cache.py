from __future__ import annotations
import json
import logging
import threading
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

_shard_locks: dict[str, threading.Lock] = {}
_shard_locks_lock = threading.Lock()


def _get_shard_lock(cache_name: str, shard: str) -> threading.Lock:
    key = f"{cache_name}:{shard}"
    with _shard_locks_lock:
        if key not in _shard_locks:
            _shard_locks[key] = threading.Lock()
        return _shard_locks[key]


def _atomic_write_json(path: Path, data: object) -> None:
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, separators=(",", ":")))
        tmp.replace(path)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise e


class ShardedCache:
    def __init__(
        self,
        root: Path,
        name: str,
        shard_fn: Callable[[str], str],
    ):
        self._root = root
        self._name = name
        self._shard_fn = shard_fn

    @property
    def _dir(self) -> Path:
        d = self._root / ".indexer" / "cache" / self._name
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def _legacy_path(self) -> Path:
        legacy_names = {
            "desc": "descriptions.json",
            "fdesc": "file_descriptions.json",
            "emb": "embeddings.json",
        }
        return self._root / ".indexer" / "cache" / legacy_names.get(self._name, f"{self._name}.json")

    def load(self) -> dict[str, dict]:
        d = self._dir
        legacy = self._legacy_path
        if legacy.exists() and not any(d.iterdir()):
            try:
                raw = json.loads(legacy.read_text())
                result = {}
                for k, v in raw.items():
                    if isinstance(v, str):
                        result[k] = {"desc": v, "sig": ""}
                    elif isinstance(v, dict):
                        result[k] = v
                return result
            except (json.JSONDecodeError, OSError):
                pass
        result = {}
        for shard_file in d.glob("*.json"):
            try:
                data = json.loads(shard_file.read_text())
                for k, v in data.items():
                    if isinstance(v, str):
                        result[k] = {"desc": v, "sig": ""}
                    elif isinstance(v, dict):
                        result[k] = v
            except (json.JSONDecodeError, OSError):
                pass
        return result

    def save(
        self,
        entries: dict[str, dict],
        current_keys: set[str] | None = None,
    ) -> None:
        d = self._dir
        legacy = self._legacy_path
        try:
            by_shard: dict[str, dict] = {}
            for key, value in entries.items():
                shard = self._shard_fn(key)
                by_shard.setdefault(shard, {})[key] = value

            if current_keys is not None:
                for shard_file in d.glob("*.json"):
                    try:
                        data = json.loads(shard_file.read_text())
                    except (json.JSONDecodeError, OSError):
                        continue
                    shard = shard_file.stem
                    stale = [k for k in data if k not in current_keys]
                    if stale:
                        for k in stale:
                            del data[k]
                    if stale or shard in by_shard:
                        by_shard[shard] = data
                        for key, value in entries.items():
                            if self._shard_fn(key) == shard:
                                by_shard[shard][key] = value

            for shard, shard_entries in by_shard.items():
                lock = _get_shard_lock(self._name, shard)
                with lock:
                    shard_path = d / f"{shard}.json"
                    existing = {}
                    if shard_path.exists() and current_keys is None:
                        try:
                            existing = json.loads(shard_path.read_text())
                        except (json.JSONDecodeError, OSError):
                            pass
                    existing.update(shard_entries)
                    if existing:
                        _atomic_write_json(shard_path, existing)
                    else:
                        try:
                            shard_path.unlink()
                        except OSError:
                            pass

            if legacy.exists():
                try:
                    legacy.unlink()
                except OSError:
                    pass
        except OSError as e:
            logger.warning("Failed to save %s cache: %s", self._name, e)
