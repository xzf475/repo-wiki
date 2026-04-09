# indexer/hooks.py
from __future__ import annotations
from pathlib import Path

HOOK_MARKER = "# managed by kiwiskil"


def _hook_command(skip_deep: bool = False) -> str:
    return "kiwiskil run --staged --skip-deep" if skip_deep else "kiwiskil run --staged"


def _hook_script_fresh(skip_deep: bool = False) -> str:
    return f"#!/bin/sh\n{HOOK_MARKER}\n{_hook_command(skip_deep)}\n"


def _hook_script_append(skip_deep: bool = False) -> str:
    return f"\n{HOOK_MARKER}\n{_hook_command(skip_deep)}\n"


def install_hook(repo_root: Path, skip_deep: bool = False) -> None:
    """Install or update the pre-commit hook.

    - Fresh install: writes a new hook script
    - Existing kiwiskil hook: updates the command in-place (e.g. adds/removes --skip-deep)
    - Existing non-kiwiskil hook: appends our block
    """
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"
    cmd = _hook_command(skip_deep)

    if hook_path.exists():
        existing = hook_path.read_text()
        if HOOK_MARKER in existing:
            # Update existing kiwiskil line in-place
            lines = existing.splitlines()
            updated = [
                cmd if (i > 0 and lines[i - 1].strip() == HOOK_MARKER) else line
                for i, line in enumerate(lines)
            ]
            hook_path.write_text("\n".join(updated) + "\n")
        else:
            hook_path.write_text(existing.rstrip() + _hook_script_append(skip_deep))
    else:
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(_hook_script_fresh(skip_deep))

    hook_path.chmod(0o755)


def remove_hook(repo_root: Path) -> None:
    """Remove the kiwiskil-managed portion of the pre-commit hook."""
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"

    if not hook_path.exists():
        return

    content = hook_path.read_text()
    if HOOK_MARKER not in content:
        return

    lines = content.splitlines()
    cleaned = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if HOOK_MARKER in line:
            skip_next = True  # skip the command line that follows
            continue
        cleaned.append(line)

    # Collapse consecutive blank lines
    result_lines = []
    prev_blank = False
    for line in cleaned:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result_lines.append(line)
        prev_blank = is_blank

    result = "\n".join(result_lines).strip()

    if result and result != "#!/bin/sh":
        hook_path.write_text(result + "\n")
    else:
        hook_path.unlink()
