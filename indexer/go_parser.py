from __future__ import annotations
from pathlib import Path
from typing import Optional
from indexer.ast_parser import ASTNode
from indexer.utils import _rel, _node_text


def _get_go_language():
    import tree_sitter_go as tsg
    from tree_sitter import Language
    return Language(tsg.language())


def _extract_go_doc(node, source: bytes) -> Optional[str]:
    prev = node.prev_named_sibling
    while prev:
        if prev.type == "comment":
            text = _node_text(prev, source).strip()
            if text.startswith("//"):
                lines = []
                for line in text.splitlines():
                    line = line.lstrip("/").strip()
                    if line:
                        lines.append(line)
                return " ".join(lines) or None
            break
        if prev.type not in ("comment", "line_comment"):
            break
        prev = prev.prev_named_sibling
    return None


def _extract_imports(tree, source: bytes) -> list[str]:
    imports = []

    def visit(node):
        if node.type == "import_declaration":
            for child in node.children:
                if child.type == "import_spec":
                    path_node = child.child_by_field_name("path")
                    if path_node:
                        imports.append(_node_text(path_node, source).strip('"'))
                elif child.type == "import_spec_list":
                    for spec in child.children:
                        if spec.type == "import_spec":
                            path_node = spec.child_by_field_name("path")
                            if path_node:
                                imports.append(_node_text(path_node, source).strip('"'))
        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return imports


def _extract_calls(node, source: bytes) -> list[str]:
    calls = set()

    def visit(n):
        if n.type == "call_expression":
            fn = n.child_by_field_name("function")
            if fn:
                if fn.type == "identifier":
                    calls.add(_node_text(fn, source))
                elif fn.type == "selector_expression":
                    field = fn.child_by_field_name("field")
                    if field:
                        calls.add(_node_text(field, source))
        for child in n.children:
            visit(child)

    visit(node)
    return list(calls)


def _get_receiver(node, source: bytes) -> Optional[str]:
    receiver = node.child_by_field_name("receiver")
    if receiver:
        for child in receiver.children:
            if child.type == "parameter_declaration":
                type_node = child.child_by_field_name("type")
                if type_node:
                    type_text = _node_text(type_node, source)
                    if type_text.startswith("*"):
                        type_text = type_text[1:]
                    return type_text
    return None


def _get_name(node, source: bytes) -> Optional[str]:
    name_node = node.child_by_field_name("name")
    if name_node:
        return _node_text(name_node, source)
    return None


def parse_go_file(path: Path, repo_root: Path) -> list[ASTNode]:
    try:
        from tree_sitter import Parser
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter not installed, skipping {path}: {e}")
        return []

    try:
        source = path.read_bytes()
        language = _get_go_language()
        parser = Parser(language)
        tree = parser.parse(source)
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter-go not installed, skipping {path}: {e}")
        return []
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to parse {path}: {e}")
        return []

    rel_path = _rel(path, repo_root)
    file_imports = _extract_imports(tree, source)
    nodes: list[ASTNode] = []

    def visit(node):
        if node.type == "function_declaration":
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
                    docstring=_extract_go_doc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type == "method_declaration":
            name = _get_name(node, source)
            receiver_type = _get_receiver(node, source)
            if name:
                if receiver_type:
                    id_str = f"{rel_path}::{receiver_type}.{name}"
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
                    docstring=_extract_go_doc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    name_node = child.child_by_field_name("name")
                    type_node = child.child_by_field_name("type")
                    if name_node and type_node:
                        name = _node_text(name_node, source)
                        if type_node.type == "struct_type":
                            nodes.append(ASTNode(
                                id=f"{rel_path}::{name}",
                                type="struct",
                                file=rel_path,
                                line_start=node.start_point[0] + 1,
                                line_end=node.end_point[0] + 1,
                                docstring=_extract_go_doc(node, source),
                                imports=list(file_imports),
                                calls=[],
                            ))
                        elif type_node.type == "interface_type":
                            nodes.append(ASTNode(
                                id=f"{rel_path}::{name}",
                                type="interface",
                                file=rel_path,
                                line_start=node.start_point[0] + 1,
                                line_end=node.end_point[0] + 1,
                                docstring=_extract_go_doc(node, source),
                                imports=list(file_imports),
                                calls=[],
                            ))
                            for method_spec in type_node.children:
                                if method_spec.type == "method_spec":
                                    spec_name = _get_name(method_spec, source)
                                    if spec_name:
                                        nodes.append(ASTNode(
                                            id=f"{rel_path}::{name}.{spec_name}",
                                            type="method_spec",
                                            file=rel_path,
                                            line_start=method_spec.start_point[0] + 1,
                                            line_end=method_spec.end_point[0] + 1,
                                            docstring=None,
                                            imports=list(file_imports),
                                            calls=[],
                                        ))
                        else:
                            nodes.append(ASTNode(
                                id=f"{rel_path}::{name}",
                                type="type",
                                file=rel_path,
                                line_start=node.start_point[0] + 1,
                                line_end=node.end_point[0] + 1,
                                docstring=_extract_go_doc(node, source),
                                imports=list(file_imports),
                                calls=[],
                            ))
            return

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return nodes
