# indexer/wiki.py
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass
class PageContext:
    group_label: str
    files: list[str]
    nodes: list  # list[ASTNode]
    descriptions: dict[str, str]
    file_descriptions: dict[str, str] = field(default_factory=dict)
    # deep enrichment fields (populated only with --deep)
    narrative: str = ""
    data_flows: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass
class IndexEntry:
    path: str
    covers: str
    entry_points: list[str]
    # deep enrichment fields (populated only with --deep)
    overview: str = ""
    flows: list[str] = field(default_factory=list)


def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_page(ctx: PageContext) -> str:
    env = _jinja_env()
    tmpl = env.get_template("page.md.j2")

    # modules dict: file -> LLM-generated purpose
    modules = {f: ctx.file_descriptions.get(f, "") for f in ctx.files}

    # Aggregate relationships across all nodes in this page
    all_calls = sorted({c for n in ctx.nodes for c in n.calls})
    all_called_by = sorted({c for n in ctx.nodes for c in n.called_by})
    all_imports = sorted({i for n in ctx.nodes for i in n.imports})

    # Entry points: only classes and top-level functions not called by anything in this page
    # Exclude private helpers (starting with _)
    entry_points = [
        n.id.split("::")[-1]
        for n in ctx.nodes
        if n.type in ("class", "function")
        and not n.called_by
        and not n.id.split("::")[-1].startswith("_")
    ]

    return tmpl.render(
        group_label=ctx.group_label,
        modules=modules,
        nodes=ctx.nodes,
        descriptions=ctx.descriptions,
        all_calls=all_calls,
        all_called_by=all_called_by,
        all_imports=all_imports,
        entry_points=entry_points,
        narrative=ctx.narrative,
        data_flows=ctx.data_flows,
        constraints=ctx.constraints,
    )


def build_index(entries: list[IndexEntry], last_commit: str, indexed_date: str, overview: str = "", flows: list[str] | None = None) -> str:
    env = _jinja_env()
    tmpl = env.get_template("index.md.j2")
    return tmpl.render(pages=entries, last_commit=last_commit, indexed_date=indexed_date, overview=overview, flows=flows or [])


def sanitize_group_label(group_label: str) -> str:
    s = group_label.replace("/", "_")
    s = re.sub(r'[:*?<>|"\s]', '_', s)
    s = s.strip("_").strip(".")
    return s or "root"

def write_page(wiki_dir: Path, group_label: str, content: str) -> Path:
    safe_name = sanitize_group_label(group_label)
    page_path = wiki_dir / f"{safe_name}.md"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(content)
    return page_path


def write_index(wiki_dir: Path, content: str) -> Path:
    wiki_dir.mkdir(parents=True, exist_ok=True)
    index_path = wiki_dir / "INDEX.md"
    index_path.write_text(content)
    return index_path
