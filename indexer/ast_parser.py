from __future__ import annotations
import ast, json, hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path

from indexer.utils import _rel

@dataclass
class ASTNode:
    id: str
    type: str
    file: str
    line_start: int
    line_end: int
    docstring: str | None
    imports: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    called_by: list[str] = field(default_factory=list)
    entry_point_kind: str = ""
    entry_point_path: str = ""

def _extract_imports(tree: ast.Module) -> list[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(f"{mod}.{alias.name}" if mod else alias.name)
    return imports

def _extract_calls(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return list(set(calls))

def _get_class_method_ids(tree: ast.Module) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ids.add(id(item))
    return ids


def _entry_point_from_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, str]:
    for dec in node.decorator_list:
        call = dec if isinstance(dec, ast.Call) else None
        func = call.func if call else dec
        name = ""
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if name in {"get", "post", "put", "patch", "delete", "route"}:
            path = ""
            if call and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
                path = call.args[0].value
            return "api", path
        if name == "command":
            return "cli", ""
    return "", ""

def parse_file(path: Path, repo_root: Path) -> list[ASTNode]:
    suffix = path.suffix.lower()
    
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        from indexer.js_parser import parse_js_file
        return parse_js_file(path, repo_root)
    
    if suffix == ".go":
        from indexer.go_parser import parse_go_file
        return parse_go_file(path, repo_root)
    
    if suffix == ".rs":
        from indexer.rust_parser import parse_rust_file
        return parse_rust_file(path, repo_root)

    if suffix == ".java":
        from indexer.java_parser import parse_java_file
        return parse_java_file(path, repo_root)

    if suffix == ".rb":
        from indexer.ruby_parser import parse_ruby_file
        return parse_ruby_file(path, repo_root)
    
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    rel_path = _rel(path, repo_root)
    file_imports = _extract_imports(tree)
    method_ids = _get_class_method_ids(tree)
    nodes: list[ASTNode] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            nodes.append(ASTNode(
                id=f"{rel_path}::{node.name}",
                type="class",
                file=rel_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                docstring=ast.get_docstring(node),
                imports=list(file_imports),
                calls=[],
            ))
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    entry_kind, entry_path = _entry_point_from_decorators(item)
                    nodes.append(ASTNode(
                        id=f"{rel_path}::{node.name}.{item.name}",
                        type="method",
                        file=rel_path,
                        line_start=item.lineno,
                        line_end=item.end_lineno or item.lineno,
                        docstring=ast.get_docstring(item),
                        imports=list(file_imports),
                        calls=_extract_calls(item),
                        entry_point_kind=entry_kind,
                        entry_point_path=entry_path,
                    ))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if id(node) not in method_ids:
                entry_kind, entry_path = _entry_point_from_decorators(node)
                nodes.append(ASTNode(
                    id=f"{rel_path}::{node.name}",
                    type="function",
                    file=rel_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    docstring=ast.get_docstring(node),
                    imports=list(file_imports),
                    calls=_extract_calls(node),
                    entry_point_kind=entry_kind,
                    entry_point_path=entry_path,
                ))

    return nodes


def compute_hash_short(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except OSError:
        return ""


def load_cached_nodes(repo_root: Path, file_hash: str) -> list[ASTNode] | None:
    p = repo_root / ".indexer" / "cache" / f"{file_hash}.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        return [ASTNode(**n) for n in data]
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def save_cached_nodes(repo_root: Path, file_hash: str, nodes: list[ASTNode]) -> None:
    from indexer.cache import _atomic_write_json
    p = repo_root / ".indexer" / "cache" / f"{file_hash}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(p, [asdict(n) for n in nodes])
