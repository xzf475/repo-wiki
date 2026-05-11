from __future__ import annotations
import fnmatch
import logging
import os
import re
import subprocess
import urllib.parse
from pathlib import Path

logger = logging.getLogger("repo-wiki-api")


class GitOperationError(Exception):
    def __init__(self, step: str, stderr: str):
        self.step = step
        self.stderr = stderr
        super().__init__(f"git {step} failed: {stderr}")


def git_fetch_checkout_pull(
    cwd: Path,
    branch: str = "",
    *,
    sanitize_fn=None,
) -> None:
    git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    git_cfg = ["-c", "http.followRedirects=true"]

    def _err(step: str, stderr: str):
        msg = sanitize_fn(stderr) if sanitize_fn else stderr
        raise GitOperationError(step, msg)

    r = subprocess.run(
        ["git"] + git_cfg + ["fetch", "--all"],
        cwd=cwd, capture_output=True, text=True, timeout=60, env=git_env,
    )
    if r.returncode != 0:
        _err("fetch", r.stderr.strip())

    if branch:
        r = subprocess.run(
            ["git"] + git_cfg + ["checkout", branch],
            cwd=cwd, capture_output=True, text=True, timeout=30, env=git_env,
        )
        if r.returncode != 0:
            _err("checkout", r.stderr.strip())
        r = subprocess.run(
            ["git"] + git_cfg + ["reset", "--hard"],
            cwd=cwd, capture_output=True, text=True, timeout=30, env=git_env,
        )
        if r.returncode != 0:
            logger.warning("git reset --hard failed: %s", r.stderr.strip())
        subprocess.run(
            ["git"] + git_cfg + ["clean", "-fd"],
            cwd=cwd, capture_output=True, text=True, timeout=30, env=git_env,
        )

    r = subprocess.run(
        ["git"] + git_cfg + ["pull", "--rebase"],
        cwd=cwd, capture_output=True, text=True, timeout=60, env=git_env,
    )
    if r.returncode != 0:
        _err("pull", r.stderr.strip())


def _detect_default_branch(repo_root: Path) -> str:
    git_env_local = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=10, env=git_env_local,
        )
        if result.returncode == 0 and result.stdout.strip():
            ref = result.stdout.strip()
            if ref.startswith("refs/remotes/origin/"):
                return ref[len("refs/remotes/origin/"):]
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "remote", "show", "origin"],
            cwd=repo_root, capture_output=True, text=True, timeout=15, env=git_env_local,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("HEAD branch:"):
                return line.split(":")[-1].strip()
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5, env=git_env_local,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "main"


def _match_branch_rule(branch_name: str, rule: str) -> bool:
    patterns = [p.strip() for p in rule.split(",")]
    return any(fnmatch.fnmatch(branch_name, p) for p in patterns)


def _discover_remote_branches(url: str, pattern: str, cwd: Path | None = None) -> list[str]:
    try:
        git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        result = subprocess.run(
            ["git", "-c", "http.followRedirects=true", "ls-remote", "--heads", url],
            cwd=cwd, capture_output=True, text=True, timeout=30, env=git_env,
        )
        if result.returncode != 0:
            return []
        branches = []
        for line in result.stdout.splitlines():
            if "\t" not in line:
                continue
            ref = line.split("\t")[-1].strip()
            if ref.startswith("refs/heads/"):
                branch_name = ref[len("refs/heads/"):]
                if _match_branch_rule(branch_name, pattern):
                    branches.append(branch_name)
        return branches
    except Exception as e:
        logger.warning("Failed to discover remote branches for %s: %s", url, e)
        return []


def _inject_credentials(
    url: str,
    username: str,
    password: str,
    token: str,
) -> str:
    if not url or url.startswith("git@") or "://" not in url:
        return url
    parsed = urllib.parse.urlparse(url)
    if token:
        netloc = f"x-access-token:{urllib.parse.quote(token, safe='')}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urllib.parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    if username and password:
        netloc = f"{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urllib.parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    return url


def _sanitize_error(error_msg: str, url: str, username: str, password: str, token: str) -> str:
    safe = error_msg
    safe = re.sub(r'https?://[^\s@]+@[^\s]+', '<REDACTED_URL>', safe)
    if url:
        safe = safe.replace(url, "<REDACTED_URL>")
    if username:
        safe = safe.replace(username, "<REDACTED_USER>")
    if password:
        safe = safe.replace(password, "<REDACTED_PASS>")
    if token:
        safe = safe.replace(token, "<REDACTED_TOKEN>")
    return safe


def _store_credentials(
    clone_dir: Path,
    url: str,
    username: str,
    password: str,
    token: str,
) -> None:
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme
    host = parsed.hostname
    if parsed.port:
        host = f"{host}:{parsed.port}"

    git_env_cred = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    r = subprocess.run(
        ["git", "remote", "set-url", "origin", url],
        cwd=clone_dir,
        capture_output=True,
        text=True,
        timeout=15,
        env=git_env_cred,
    )
    if r.returncode != 0:
        logger.warning("git remote set-url failed: %s", r.stderr.strip())

    if not (username or password or token):
        return

    credential_file = clone_dir / ".git" / "credentials"
    cred_store_path = str(credential_file)

    subprocess.run(
        ["git", "config", "credential.helper", f"store --file={cred_store_path}"],
        cwd=clone_dir,
        capture_output=True,
        text=True,
        timeout=15,
        env=git_env_cred,
    )

    if token:
        cred_line = f"{scheme}://x-access-token:{urllib.parse.quote(token, safe='')}@{host}"
    elif username and password:
        cred_line = f"{scheme}://{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@{host}"
    else:
        return

    existing = ""
    if credential_file.exists():
        existing = credential_file.read_text()
    if cred_line not in existing:
        tmp = credential_file.with_suffix(".tmp")
        tmp.write_text((existing.rstrip("\n") + "\n" + cred_line if existing.strip() else cred_line) + "\n")
        tmp.replace(credential_file)
        os.chmod(credential_file, 0o600)
