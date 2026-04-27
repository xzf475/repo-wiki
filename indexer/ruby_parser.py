from __future__ import annotations
from pathlib import Path
from typing import Optional
from indexer.ast_parser import ASTNode
from indexer.utils import _rel, _node_text


def _get_ruby_language():
    import tree_sitter_ruby as tsrb
    from tree_sitter import Language
    return Language(tsrb.language())


def _extract_ruby_doc(node, source: bytes) -> Optional[str]:
    prev = node.prev_named_sibling
    while prev:
        if prev.type == "comment":
            text = _node_text(prev, source).strip()
            if text.startswith("#"):
                lines = [line.strip().lstrip("#").strip() for line in text.splitlines() if line.strip().lstrip("#").strip()]
                return " ".join(lines) or None
            break
        if prev.type != "comment":
            break
        prev = prev.prev_named_sibling
    return None


def _extract_imports(tree, source: bytes) -> list[str]:
    imports = []
    def visit(node):
        if node.type in ("require", "require_relative"):
            text = _node_text(node, source).split("\n")[0][:80]
            imports.append(text)
        for child in node.children:
            visit(child)
    visit(tree.root_node)
    return imports


def _extract_calls(node, source: bytes) -> list[str]:
    calls = set()
    def visit(n):
        if n.type == "call":
            method_node = n.child_by_field_name("method")
            if method_node:
                calls.add(_node_text(method_node, source))
        for child in n.children:
            visit(child)
    visit(node)
    return list(calls)


def _get_name(node, source: bytes) -> Optional[str]:
    name_node = node.child_by_field_name("name")
    if name_node:
        return _node_text(name_node, source)
    return None


def parse_ruby_file(path: Path, repo_root: Path) -> list[ASTNode]:
    try:
        from tree_sitter import Parser
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter not installed, skipping {path}: {e}")
        return []

    try:
        source = path.read_bytes()
        language = _get_ruby_language()
        parser = Parser(language)
        tree = parser.parse(source)
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter-ruby not installed, skipping {path}: {e}")
        return []
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to parse {path}: {e}")
        return []

    rel_path = _rel(path, repo_root)
    file_imports = _extract_imports(tree, source)
    nodes: list[ASTNode] = []

    def visit(node, class_name: Optional[str] = None, module_name: Optional[str] = None):
        if node.type == "class":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="class",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_ruby_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        visit(child, class_name=name, module_name=module_name)
            return

        elif node.type == "method" and class_name:
            name = _get_name(node, source)
            if name:
                body = node.child_by_field_name("body")
                calls = _extract_calls(body, source) if body else []
                nodes.append(ASTNode(
                    id=f"{rel_path}::{class_name}.{name}",
                    type="method",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_ruby_doc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type in ("singleton_method", "method") and not class_name:
            name = _get_name(node, source)
            if name:
                body = node.child_by_field_name("body")
                calls = _extract_calls(body, source) if body else []
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="function",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_ruby_doc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type == "module":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="module",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_ruby_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        visit(child, class_name=class_name, module_name=name)
            return

        for child in node.children:
            visit(child, class_name=class_name, module_name=module_name)

    visit(tree.root_node)
    return nodes
