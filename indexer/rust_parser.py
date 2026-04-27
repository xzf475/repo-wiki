from __future__ import annotations
from pathlib import Path
from typing import Optional
from indexer.ast_parser import ASTNode
from indexer.utils import _rel, _node_text


def _get_rust_language():
    import tree_sitter_rust as tsr
    from tree_sitter import Language
    return Language(tsr.language())


def _extract_rust_doc(node, source: bytes) -> Optional[str]:
    prev = node.prev_named_sibling
    while prev:
        if prev.type == "line_comment":
            text = _node_text(prev, source).strip()
            if text.startswith("///") or text.startswith("//!"):
                lines = [line.strip().lstrip("/").strip() for line in text.splitlines() if line.strip().lstrip("/").strip()]
                return " ".join(lines) or None
            break
        elif prev.type == "block_comment":
            text = _node_text(prev, source).strip()
            if text.startswith("/**") or text.startswith("/*!"):
                inner = text.strip().removeprefix("/**").removesuffix("*/").removeprefix("/*!").removesuffix("*/")
                lines = []
                for line in inner.splitlines():
                    line = line.strip().strip("*").strip()
                    if line:
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
        if node.type == "use_declaration":
            imports.append(_node_text(node, source).split("\n")[0][:80])
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
                elif fn.type == "field_expression":
                    field = fn.child_by_field_name("field")
                    if field:
                        calls.add(_node_text(field, source))
                elif fn.type == "scoped_identifier":
                    name_node = fn.child_by_field_name("name")
                    if name_node:
                        calls.add(_node_text(name_node, source))
        for child in n.children:
            visit(child)
    visit(node)
    return list(calls)


def _get_name(node, source: bytes) -> Optional[str]:
    name_node = node.child_by_field_name("name")
    if name_node:
        return _node_text(name_node, source)
    return None


def parse_rust_file(path: Path, repo_root: Path) -> list[ASTNode]:
    try:
        from tree_sitter import Parser
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter not installed, skipping {path}: {e}")
        return []

    try:
        source = path.read_bytes()
        language = _get_rust_language()
        parser = Parser(language)
        tree = parser.parse(source)
    except ImportError as e:
        import warnings
        warnings.warn(f"tree-sitter-rust not installed, skipping {path}: {e}")
        return []
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to parse {path}: {e}")
        return []

    rel_path = _rel(path, repo_root)
    file_imports = _extract_imports(tree, source)
    nodes: list[ASTNode] = []

    def visit(node):
        if node.type == "function_item":
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
                    docstring=_extract_rust_doc(node, source),
                    imports=list(file_imports),
                    calls=calls,
                ))
            return

        elif node.type == "struct_item":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="struct",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_rust_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
            return

        elif node.type == "impl_item":
            impl_type = node.child_by_field_name("type")
            type_name = _node_text(impl_type, source) if impl_type else None

            decl_list = next((c for c in node.children if c.type == "declaration_list"), None)
            if decl_list:
                for child in decl_list.children:
                    if child.type == "function_item":
                        name = _get_name(child, source)
                        if name:
                            body = child.child_by_field_name("body")
                            calls = _extract_calls(body, source) if body else []
                            nodes.append(ASTNode(
                                id=f"{rel_path}::{type_name}.{name}" if type_name else f"{rel_path}::{name}",
                                type="method",
                                file=rel_path,
                                line_start=child.start_point[0] + 1,
                                line_end=child.end_point[0] + 1,
                                docstring=_extract_rust_doc(child, source),
                                imports=list(file_imports),
                                calls=calls,
                            ))
            return

        elif node.type == "trait_item":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="trait",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_rust_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
                decl_list = next((c for c in node.children if c.type == "declaration_list"), None)
                if decl_list:
                    for child in decl_list.children:
                        if child.type == "function_signature_item":
                            sig_name = _get_name(child, source)
                            if sig_name:
                                nodes.append(ASTNode(
                                    id=f"{rel_path}::{name}.{sig_name}",
                                    type="method_spec",
                                    file=rel_path,
                                    line_start=child.start_point[0] + 1,
                                    line_end=child.end_point[0] + 1,
                                    docstring=None,
                                    imports=list(file_imports),
                                    calls=[],
                                ))
            return

        elif node.type == "enum_item":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="enum",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_rust_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
            return

        elif node.type == "type_item":
            name = _get_name(node, source)
            if name:
                nodes.append(ASTNode(
                    id=f"{rel_path}::{name}",
                    type="type",
                    file=rel_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    docstring=_extract_rust_doc(node, source),
                    imports=list(file_imports),
                    calls=[],
                ))
            return

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return nodes
