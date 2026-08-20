from __future__ import annotations
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def _run(cmd: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace", env=_GIT_ENV)
        if result.returncode != 0:
            logger.warning("git command failed (rc=%d): %s\nstderr: %s", result.returncode, " ".join(cmd), result.stderr.strip())
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.warning("git command timed out: %s", " ".join(cmd))
        return ""
    except (FileNotFoundError, OSError) as e:
        logger.warning("git command error: %s", e)
        return ""


def current_branch(repo_root: Path) -> str | None:
    out = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if out and out != "HEAD":
        return out
    return None

def is_git_repo(repo_root: Path) -> bool:
    return bool(_run(["git", "rev-parse", "--git-dir"], cwd=repo_root))
