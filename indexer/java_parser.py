from __future__ import annotations
from pathlib import Path
from typing import Optional
from indexer.ast_parser import ASTNode
from indexer.utils import _rel, _node_text


def _get_java_language():
    import tree_sitter_java as tsj
    from tree_sitter import Language
    return Language(tsj.language())


def _extract_javadoc(node, source: bytes) -> Optional[str]:
    prev = node.prev_named_sibling
    while prev:
        if prev.type == "block_comment":
            text = _node_text(prev, source).strip()
            if text.startswith("/**"):
                inner = text.strip().removeprefix("/**").removesuffix("*/")
                lines = []
                for line in inner.splitlines():
                    line = line.strip().strip("*").strip()
                    if line and not line.startswith("@"):
                        lines.append(line)
                return " ".join(lines) or None
            break
        if prev.type not in ("line_comment", "block_comment"):
            break
        prev = prev.prev_named_sibling
    return None


def _extract_imports(tree, source: bytes) -> list[str]:
    imports = []
    def visit(node):
        if node.type == "import_declaration":
            imports.append(_node_text(node, source).split("\n")[0][:80])
        for child in node.children:
            visit(child)
    visit(tree.root_node)
    return imports


def _extract_calls(node, source: bytes) -> list[str]:
    calls = set()
    def visit(n):
        if n.type == "method_invocation":
            name_node = n.child_by_field_name("name")
            if name_node:
                calls.add(_node_text(name_node, source))
            else:
                obj_node = n.child_by_field_name("object")
                if obj_node and obj_node.type == "identifier":
                    calls.add(_node_text(obj_node, source))
        elif n.type == "object_creation_expression":
            type_node = n.child_by_field_name("type")
            if type_node:
                calls.add(_node_text(type_node, source))
        for child in n.children:
            visit(child)
    visit(node)
    return list(calls)


def _get_name(node, source: bytes) -> Optional[str]:
    name_node = node.child_by_field_name("name")
    if name_node:
        return _node_text(name_node, source)
    return None


def _get_type_name(node, source: bytes) -> Optional[str]:
    type_node = node.child_by_field_name("type")
    if type_node:
        return _node_text(type_node, source)
    return None


def parse_java_file(path: Path, repo_root: Path) -> list[ASTNode]:
    try:
        from tree_sitter import Parser
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter not installed, skipping {path}: {e}")
        return []

    try:
        source = path.read_bytes()
        language = _get_java_language()
        parser = Parser(language)
        tree = parser.parse(source)
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter-java not installed, skipping {path}: {e}")
        return []
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to parse {path}: {e}")
        return []

    rel_path = _rel(path, repo_root)
    file_imports = _extract_imports(tree, source)
    nodes: list[ASTNode] = []

    def visit(node, class_name: Optional[str] = None, interface_name: Optional[str] = None):
        if node.type == "class_declaration":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="class",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_javadoc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        visit(child, class_name=name)
            return

        elif node.type == "method_declaration":
            name = _get_name(node, source)
            if name:
                if class_name:
                    id_str = f"{rel_path}::{class_name}.{name}"
                    node_type = "method"
                else:
                    id_str = f"{rel_path}::{name}"
                    node_type = "function"
                body = node.child_by_field_name("body")
                calls = _extract_calls(body, source) if body else []
                nodes.append(ASTNode(
                    id=id_str,
                    type=node_type,
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_javadoc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type == "interface_declaration":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="interface",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_javadoc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        visit(child, interface_name=name)
            return

        elif node.type == "enum_declaration":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="enum",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_javadoc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
            return

        for child in node.children:
            visit(child, class_name=class_name, interface_name=interface_name)

    visit(tree.root_node)
    return nodes
