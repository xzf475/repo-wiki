from __future__ import annotations
from collections import defaultdict
from pathlib import Path


def density_group(files: list[str], merge_threshold: int = 6) -> dict[str, str]:
    if not files:
        return {}

    def folder_of(f: str) -> str:
        parent = str(Path(f).parent)
        return "." if parent == "." else parent

    def prefixes(folder: str) -> list[str]:
        if folder == ".":
            return ["."]
        parts = folder.split("/")
        return ["/".join(parts[:i]) for i in range(len(parts), 0, -1)]

    prefix_count: dict[str, int] = defaultdict(int)
    for f in files:
        folder = folder_of(f)
        for prefix in prefixes(folder):
            prefix_count[prefix] += 1

    def resolve_group(f: str) -> str:
        folder = folder_of(f)
        all_prefixes = prefixes(folder)

        for prefix in all_prefixes:
            if prefix_count[prefix] >= merge_threshold:
                return prefix

        if len(all_prefixes) > 1:
            return all_prefixes[-2]
        return "."

    return {f: resolve_group(f) for f in files}
