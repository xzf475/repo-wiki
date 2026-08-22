from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from indexer.ast_parser import ASTNode
from indexer.config import Config
from indexer.grouper import density_group
from indexer.repository_index import IndexScope, RepositoryIndex
from indexer.wiki import (
    IndexEntry,
    PageContext,
    _atomic_write_text,
    _jinja_env,
    build_index,
    build_page,
    sanitize_group_label,
    write_index,
    write_page,
)


@dataclass(frozen=True)
class ProjectionReport:
    repo: str
    branch: str
    generation: int
    tree_id: str
    pages: int
    files: int
    symbols: int


def write_repository_projection(
    root: Path,
    config: Config,
    index: RepositoryIndex,
    scope: IndexScope,
) -> ProjectionReport:
    """Render Wiki and Skill files from one already-published generation."""
    status = index.inspect(scope, resolve_relations=False)
    if not status.exists or status.generation is None:
        raise ValueError(f"index scope {scope.repo}:{scope.branch} has no published generation")

    files = list(index.files(scope))
    records = index.symbols(scope)
    nodes = [
        ASTNode(
            id=record.component_id,
            type=record.type,
            file=record.file,
            line_start=record.line_start,
            line_end=record.line_end,
            docstring=record.docstring or None,
            source=record.source,
            imports=list(record.imports),
            calls=list(record.calls),
            called_by=list(record.called_by),
            entry_point_kind=record.entry_point_kind,
            entry_point_path=record.entry_point_path,
        )
        for record in records
    ]
    groups = density_group(files, merge_threshold=config.merge_threshold)
    grouped_files: dict[str, list[str]] = {}
    grouped_nodes: dict[str, list[ASTNode]] = {}
    for path in files:
        group = groups.get(path, path)
        grouped_files.setdefault(group, []).append(path)
        grouped_nodes.setdefault(group, [])
    for node in nodes:
        grouped_nodes.setdefault(groups.get(node.file, node.file), []).append(node)

    descriptions = {
        node.id: node.docstring or ""
        for node in nodes
    }
    wiki_dir = root / config.wiki_dir
    entries: list[IndexEntry] = []
    projected_pages: set[Path] = set()
    for group in sorted(grouped_files):
        group_nodes = grouped_nodes.get(group, [])
        content = build_page(PageContext(
            group_label=group,
            files=sorted(grouped_files[group]),
            nodes=group_nodes,
            descriptions=descriptions,
        ))
        page = write_page(wiki_dir, group, content)
        projected_pages.add(page.resolve())
        entries.append(IndexEntry(
            path=str(page.relative_to(root)),
            covers=", ".join(sorted(grouped_files[group])),
            entry_points=[
                node.id.split("::")[-1]
                for node in group_nodes
                if not node.called_by
            ],
            group_label=group,
        ))

    for existing_page in wiki_dir.glob("*.md"):
        if existing_page.name != "INDEX.md" and existing_page.resolve() not in projected_pages:
            existing_page.unlink()

    indexed_date = datetime.now(UTC).strftime("%Y-%m-%d")
    overview = (
        f"{scope.repo}:{scope.branch} generation {status.generation} "
        f"at tree {status.tree_id}"
    )
    write_index(
        wiki_dir,
        build_index(entries, status.tree_id, indexed_date, overview=overview),
    )
    _write_skill(
        root,
        config,
        entries,
        overview=overview,
        total_symbols=len(nodes),
        total_files=len(files),
        tree_id=status.tree_id,
        indexed_date=indexed_date,
    )
    return ProjectionReport(
        repo=scope.repo,
        branch=scope.branch,
        generation=status.generation,
        tree_id=status.tree_id,
        pages=len(entries),
        files=len(files),
        symbols=len(nodes),
    )


def _write_skill(
    root: Path,
    config: Config,
    entries: list[IndexEntry],
    *,
    overview: str,
    total_symbols: int,
    total_files: int,
    tree_id: str,
    indexed_date: str,
) -> None:
    pages = [
        {
            "label": sanitize_group_label(entry.group_label),
            "path": entry.path,
            "covers": entry.covers,
            "entry_points": entry.entry_points[:5],
            "enrichment": {},
        }
        for entry in entries
    ]
    content = _jinja_env().get_template("skill.md.j2").render(
        wiki_dir=config.wiki_dir,
        pages=pages,
        overview=overview,
        key_flows=[],
        total_symbols=total_symbols,
        total_files=total_files,
        commit=tree_id,
        indexed_date=indexed_date,
    )
    skill_dir = root / ".indexer" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(skill_dir / "codebase.md", content)


__all__ = ["ProjectionReport", "write_repository_projection"]
