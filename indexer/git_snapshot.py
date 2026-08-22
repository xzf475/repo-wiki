from __future__ import annotations

import subprocess
import tempfile
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from uuid import uuid4


SUPPORTED_SUFFIXES = frozenset({
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".java",
    ".rb",
})
STAGED_REVISION = "@staged"
WORKTREE_REVISION = "@worktree"
GENERATED_PATHS = (
    ".indexer/skills",
    ".indexer/state",
    "wiki",
)
SNAPSHOT_LEASE_SECONDS = 60 * 60


class GitSnapshotError(RuntimeError):
    pass


@dataclass(frozen=True)
class TreeEntry:
    path: str
    blob_id: str


@dataclass(frozen=True)
class TreeDelta:
    changed: tuple[TreeEntry, ...]
    removed: tuple[str, ...]
    entries_scanned: int


class GitSnapshot:
    """Read immutable Git trees without checking them out."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self._snapshot_environment: dict[str, str] | None = None
        self._snapshot_leases: list[Path] = []

    def __enter__(self) -> "GitSnapshot":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._snapshot_environment = None
        self.release_snapshot_leases(tuple(self._snapshot_leases))
        self._snapshot_leases.clear()

    def detach_snapshot_leases(self) -> tuple[Path, ...]:
        leases = tuple(self._snapshot_leases)
        self._snapshot_leases.clear()
        return leases

    @staticmethod
    def release_snapshot_leases(leases: tuple[Path, ...]) -> None:
        for lease in leases:
            try:
                lease.unlink(missing_ok=True)
            except OSError:
                continue

    def resolve_tree(self, revision: str) -> str:
        if not revision.strip():
            raise GitSnapshotError("revision must not be empty")
        if revision == STAGED_REVISION:
            return self._capture_staged_tree()
        if revision == WORKTREE_REVISION:
            return self._capture_worktree_tree()
        output = self._run_text(["rev-parse", "--verify", f"{revision}^{{tree}}"])
        tree_id = output.strip()
        if not tree_id:
            raise GitSnapshotError(f"revision {revision!r} did not resolve to a tree")
        return tree_id

    def initial_delta(self, tree_id: str) -> TreeDelta:
        entries = self._list_tree(tree_id)
        indexable = tuple(sorted(
            (entry for entry in entries if _is_indexable(entry.path)),
            key=lambda entry: entry.path,
        ))
        return TreeDelta(changed=indexable, removed=(), entries_scanned=len(entries))

    def delta(self, previous_tree: str, tree_id: str) -> TreeDelta:
        if previous_tree == tree_id:
            return TreeDelta(changed=(), removed=(), entries_scanned=0)

        output = self._run_bytes([
            "diff-tree",
            "-r",
            "--no-commit-id",
            "--name-status",
            "-z",
            "--no-renames",
            previous_tree,
            tree_id,
        ])
        tokens = output.split(b"\0")
        changed_paths: list[str] = []
        removed_paths: list[str] = []
        entries_scanned = 0
        index = 0
        while index < len(tokens) and tokens[index]:
            status = tokens[index].decode("ascii", errors="replace")
            if index + 1 >= len(tokens):
                raise GitSnapshotError("git diff-tree returned an incomplete record")
            path = tokens[index + 1].decode("utf-8", errors="surrogateescape")
            index += 2
            entries_scanned += 1
            if status.startswith("D"):
                if _is_indexable(path):
                    removed_paths.append(path)
            elif _is_indexable(path):
                changed_paths.append(path)

        entries = self._entries_for_paths(tree_id, changed_paths)
        missing = sorted(set(changed_paths) - entries.keys())
        if missing:
            raise GitSnapshotError(f"changed paths missing from target tree: {', '.join(missing)}")
        return TreeDelta(
            changed=tuple(entries[path] for path in sorted(entries)),
            removed=tuple(sorted(set(removed_paths))),
            entries_scanned=entries_scanned,
        )

    def read_blobs(self, blob_ids: list[str] | tuple[str, ...]) -> dict[str, bytes]:
        unique_ids = tuple(dict.fromkeys(blob_ids))
        if not unique_ids:
            return {}
        request = "".join(f"{blob_id}\n" for blob_id in unique_ids).encode("ascii")
        output = self._run_bytes(["cat-file", "--batch"], input_bytes=request)
        offset = 0
        blobs: dict[str, bytes] = {}
        for requested_id in unique_ids:
            header_end = output.find(b"\n", offset)
            if header_end < 0:
                raise GitSnapshotError("git cat-file returned an incomplete header")
            header = output[offset:header_end].decode("ascii", errors="replace")
            offset = header_end + 1
            parts = header.split()
            if len(parts) != 3 or parts[1] != "blob":
                raise GitSnapshotError(f"unable to read blob {requested_id}: {header}")
            size = int(parts[2])
            end = offset + size
            if end > len(output):
                raise GitSnapshotError(f"git cat-file truncated blob {requested_id}")
            blobs[requested_id] = output[offset:end]
            offset = end
            if offset >= len(output) or output[offset:offset + 1] != b"\n":
                raise GitSnapshotError(f"git cat-file omitted separator for blob {requested_id}")
            offset += 1
        return blobs

    def prune_snapshots(self, retained_tree_ids: tuple[str, ...]) -> int:
        """Remove loose synthetic objects unreachable from retained generations."""
        snapshot_objects = self.root / ".indexer" / "state" / "git-objects"
        if not snapshot_objects.exists():
            return 0
        leased_tree_ids = self._active_snapshot_leases()
        if leased_tree_ids is None:
            return 0
        retained_tree_ids = tuple(dict.fromkeys((
            *retained_tree_ids,
            *leased_tree_ids,
        )))
        before = sum(path.is_file() for path in snapshot_objects.rglob("*"))
        environment = self._object_environment()
        self._run_bytes(
            ["prune", "--expire=now", "--", *retained_tree_ids],
            environment=environment,
        )
        after = sum(path.is_file() for path in snapshot_objects.rglob("*"))
        return max(0, before - after)

    def _active_snapshot_leases(self) -> tuple[str, ...] | None:
        lease_root = self.root / ".indexer" / "state" / "git-object-leases"
        if not lease_root.exists():
            return ()
        now = time.time()
        tree_ids: list[str] = []
        for lease in lease_root.iterdir():
            if not lease.is_file():
                continue
            try:
                if now - lease.stat().st_mtime > SNAPSHOT_LEASE_SECONDS:
                    lease.unlink(missing_ok=True)
                    continue
                tree_id = lease.read_text().strip()
            except OSError:
                continue
            if not tree_id:
                return None
            tree_ids.append(tree_id)
        return tuple(dict.fromkeys(tree_ids))

    def _list_tree(self, tree_id: str, pathspecs: list[str] | None = None) -> list[TreeEntry]:
        args = ["ls-tree", "-r", "-z", "--full-tree", tree_id]
        if pathspecs:
            args.append("--")
            args.extend(f":(literal){path}" for path in pathspecs)
        output = self._run_bytes(args)
        entries: list[TreeEntry] = []
        for record in output.split(b"\0"):
            if not record:
                continue
            try:
                metadata, raw_path = record.split(b"\t", 1)
                _mode, object_type, raw_object_id = metadata.split(b" ", 2)
            except ValueError as error:
                raise GitSnapshotError("git ls-tree returned an invalid record") from error
            if object_type != b"blob":
                continue
            entries.append(TreeEntry(
                path=raw_path.decode("utf-8", errors="surrogateescape"),
                blob_id=raw_object_id.decode("ascii"),
            ))
        return entries

    def _entries_for_paths(self, tree_id: str, paths: list[str]) -> dict[str, TreeEntry]:
        entries: dict[str, TreeEntry] = {}
        for start in range(0, len(paths), 256):
            for entry in self._list_tree(tree_id, paths[start:start + 256]):
                entries[entry.path] = entry
        return entries

    def _run_text(self, args: list[str]) -> str:
        return self._run_bytes(args).decode("utf-8", errors="replace")

    def _capture_worktree_tree(self) -> str:
        self.close()
        lease = self._begin_snapshot_lease()
        object_environment = self._object_environment()
        self._snapshot_environment = object_environment
        with tempfile.TemporaryDirectory(prefix="repo-wiki-index-") as directory:
            environment = {
                **object_environment,
                "GIT_INDEX_FILE": str(Path(directory) / "index"),
            }
            self._run_bytes(["read-tree", "HEAD"], environment=environment)
            self._run_bytes(["add", "-A", "--", "."], environment=environment)
            self._remove_generated_paths(environment)
            tree_id = self._run_bytes(
                ["write-tree"],
                environment=environment,
            ).decode("ascii", errors="replace").strip()
        if not tree_id:
            raise GitSnapshotError("unable to capture worktree tree")
        lease.write_text(tree_id)
        return tree_id

    def _capture_staged_tree(self) -> str:
        self.close()
        lease = self._begin_snapshot_lease()
        raw_index_path = Path(
            self._run_text(["rev-parse", "--git-path", "index"]).strip()
        )
        index_path = (
            raw_index_path
            if raw_index_path.is_absolute()
            else (self.root / raw_index_path).resolve()
        )
        if not index_path.exists():
            raise GitSnapshotError("unable to locate the Git index")
        object_environment = self._object_environment()
        self._snapshot_environment = object_environment
        with tempfile.TemporaryDirectory(prefix="repo-wiki-index-") as directory:
            temporary_index = Path(directory) / "index"
            shutil.copyfile(index_path, temporary_index)
            environment = {
                **object_environment,
                "GIT_INDEX_FILE": str(temporary_index),
            }
            self._remove_generated_paths(environment)
            tree_id = self._run_bytes(
                ["write-tree"],
                environment=environment,
            ).decode("ascii", errors="replace").strip()
        if not tree_id:
            raise GitSnapshotError("unable to capture staged tree")
        lease.write_text(tree_id)
        return tree_id

    def _begin_snapshot_lease(self) -> Path:
        lease_root = self.root / ".indexer" / "state" / "git-object-leases"
        lease_root.mkdir(parents=True, exist_ok=True)
        lease = lease_root / uuid4().hex
        lease.touch(exist_ok=False)
        self._snapshot_leases.append(lease)
        return lease

    def _object_environment(self) -> dict[str, str]:
        snapshot_objects = self.root / ".indexer" / "state" / "git-objects"
        snapshot_objects.mkdir(parents=True, exist_ok=True)
        shared_objects = Path(
            self._run_text(["rev-parse", "--git-path", "objects"]).strip()
        )
        if not shared_objects.is_absolute():
            shared_objects = (self.root / shared_objects).resolve()
        return {
            **os.environ,
            "GIT_OBJECT_DIRECTORY": str(snapshot_objects),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(shared_objects),
        }

    def _remove_generated_paths(self, environment: dict[str, str]) -> None:
        self._run_bytes(
            [
                "rm",
                "--cached",
                "-r",
                "--ignore-unmatch",
                "--",
                *GENERATED_PATHS,
            ],
            environment=environment,
        )

    def _run_bytes(
        self,
        args: list[str],
        input_bytes: bytes | None = None,
        *,
        environment: dict[str, str] | None = None,
    ) -> bytes:
        selected_environment = environment or self._snapshot_environment
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.root,
                input=input_bytes,
                capture_output=True,
                timeout=120,
                env=selected_environment,
            )
        except subprocess.TimeoutExpired as error:
            raise GitSnapshotError(f"git {' '.join(args)} timed out") from error
        except (FileNotFoundError, OSError) as error:
            raise GitSnapshotError(str(error)) from error
        if result.returncode != 0:
            message = result.stderr.decode("utf-8", errors="replace").strip()
            raise GitSnapshotError(message or f"git {' '.join(args)} exited {result.returncode}")
        return result.stdout


def _is_indexable(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in SUPPORTED_SUFFIXES


__all__ = [
    "GitSnapshot",
    "GitSnapshotError",
    "GENERATED_PATHS",
    "STAGED_REVISION",
    "SUPPORTED_SUFFIXES",
    "TreeDelta",
    "TreeEntry",
    "WORKTREE_REVISION",
]
