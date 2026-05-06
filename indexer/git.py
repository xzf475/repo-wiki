from __future__ import annotations
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _run(cmd: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            logger.warning("git command failed (rc=%d): %s\nstderr: %s", result.returncode, " ".join(cmd), result.stderr.strip())
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.warning("git command timed out: %s", " ".join(cmd))
        return ""
    except (FileNotFoundError, OSError) as e:
        logger.warning("git command error: %s", e)
        return ""

def current_commit(repo_root: Path) -> Optional[str]:
    out = _run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    return out if out else None

def current_branch(repo_root: Path) -> Optional[str]:
    out = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if out and out != "HEAD":
        return out
    return None

def staged_files(repo_root: Path) -> list[str]:
    out = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], cwd=repo_root)
    return [line for line in out.splitlines() if line]

def changed_files_since(repo_root: Path, since_commit: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACM", since_commit, "HEAD"],
        cwd=repo_root, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        logger.warning("git diff failed for commit %s: %s", since_commit, result.stderr.strip())
        raise ValueError(f"Invalid commit reference: {since_commit}")
    return [line for line in result.stdout.strip().splitlines() if line]

def all_tracked_files(repo_root: Path) -> list[str]:
    out = _run(["git", "ls-files"], cwd=repo_root)
    return [line for line in out.splitlines() if line]

def is_git_repo(repo_root: Path) -> bool:
    return bool(_run(["git", "rev-parse", "--git-dir"], cwd=repo_root))
