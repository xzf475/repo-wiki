# indexer/hooks.py
from __future__ import annotations
from pathlib import Path

HOOK_MARKER = "# managed by kiwiskil"
HOOK_CONTENT = "kiwiskil run --staged"

# Used for fresh install (no existing hook)
HOOK_SCRIPT_FRESH = f"""\
#!/bin/sh
{HOOK_MARKER}
{HOOK_CONTENT}
"""

# Used when appending to existing hook (no shebang)
HOOK_SCRIPT_APPEND = f"""
{HOOK_MARKER}
{HOOK_CONTENT}
"""


def install_hook(repo_root: Path) -> None:
    """Install the pre-commit hook in repo_root/.git/hooks/pre-commit.

    If a pre-commit hook already exists and is not managed by kiwiskil,
    append our script to it rather than overwriting.
    If already installed, do nothing.
    """
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"

    if hook_path.exists():
        existing = hook_path.read_text()
        if HOOK_MARKER in existing:
            return  # already installed, nothing to do
        # Append to existing hook (use HOOK_SCRIPT_APPEND without shebang)
        updated = existing.rstrip() + "\n\n" + HOOK_SCRIPT_APPEND
        hook_path.write_text(updated)
    else:
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(HOOK_SCRIPT_FRESH)

    hook_path.chmod(0o755)


def remove_hook(repo_root: Path) -> None:
    """Remove the kiwiskil-managed portion of the pre-commit hook.

    If the hook consists entirely of our script, delete the file.
    If our script was appended to an existing hook, remove only our lines.
    If not installed, do nothing.
    """
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"

    if not hook_path.exists():
        return

    content = hook_path.read_text()
    if HOOK_MARKER not in content:
        return  # not managed by us

    # Remove lines added by kiwiskil
    lines = content.splitlines()
    cleaned = [
        line for line in lines
        if HOOK_MARKER not in line and HOOK_CONTENT not in line
    ]

    # Collapse multiple consecutive blank lines into one
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
