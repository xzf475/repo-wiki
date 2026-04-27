from __future__ import annotations
import os
import threading
from pathlib import Path


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _node_text(node, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


_env_lock = threading.Lock()
_env_loaded = False


def load_env_file() -> None:
    global _env_loaded
    with _env_lock:
        if _env_loaded:
            return
        candidates = [
            Path(__file__).resolve().parent.parent / ".env",
            Path.cwd() / ".env",
        ]
        for env_path in candidates:
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and key not in os.environ:
                        os.environ[key] = value
                break
        _env_loaded = True
