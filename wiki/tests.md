# tests/

## Overview

The AST parser module provides a language-agnostic parsing interface that converts source code files into a unified list of `Node` objects, each capturing name, type, docstring, imports, and calls. It supports Python, Rust, Java, and Ruby by delegating to language-specific tree‑sitter grammars or similar backends. The parser is the foundation for downstream modules: `grouper` organizes nodes into hierarchies, `wiki` generates documentation from parsed structures, and `manifest` tracks file‑level metadata. Caching via `save_cached_nodes` / `load_cached_nodes` avoids redundant re‑parsing of unchanged files, making repeated analysis fast.

## Modules
| File | Purpose |
|------|---------|
| tests/test_grouper.py | Tests for file grouping logic |
| tests/test_wiki.py | Tests for wiki page generation |
| tests/test_ast_parser.py | Tests for AST parser functions |
| tests/test_config.py | Tests for configuration loading |
| tests/test_manifest.py | Tests for manifest management |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/test_ast_parser.py::test_parse_returns_nodes` | function | Asserts parse_file returns node list. |
| `tests/test_ast_parser.py::test_function_node` | function | Asserts node list contains function node. |
| `tests/test_ast_parser.py::test_method_node` | function | Asserts node list contains method node. |
| `tests/test_ast_parser.py::test_class_node` | function | Asserts node list contains class node. |
| `tests/test_ast_parser.py::test_docstring_extracted` | function | Asserts extracted node has correct docstring. |
| `tests/test_ast_parser.py::test_imports_extracted` | function | Asserts node imports are extracted. |
| `tests/test_ast_parser.py::test_calls_extracted` | function | Asserts node calls are extracted. |
| `tests/test_ast_parser.py::test_cache_roundtrip` | function | Tests save/load cached nodes roundtrip. |
| `tests/test_ast_parser.py::test_rust_parse_returns_nodes` | function | Asserts Rust parse returns nodes. |
| `tests/test_ast_parser.py::test_rust_function_node` | function | Asserts Rust parse contains function node. |
| `tests/test_ast_parser.py::test_rust_struct_node` | function | Asserts Rust parse contains struct node. |
| `tests/test_ast_parser.py::test_rust_method_node` | function | Asserts Rust parse contains method node. |
| `tests/test_ast_parser.py::test_rust_trait_node` | function | Asserts Rust parse contains trait node. |
| `tests/test_ast_parser.py::test_rust_trait_method_spec` | function | Asserts Rust parse contains trait method spec. |
| `tests/test_ast_parser.py::test_rust_enum_node` | function | Parses Rust file and asserts existence of an enum node |
| `tests/test_ast_parser.py::test_rust_type_alias` | function | Parses Rust file and asserts existence of a type alias node |
| `tests/test_ast_parser.py::test_rust_docstring_extracted` | function | Parses Rust file and verifies first node has docstring |
| `tests/test_ast_parser.py::test_rust_imports_extracted` | function | Parses Rust file and verifies imports are extracted as Import nodes |
| `tests/test_ast_parser.py::test_java_parse_returns_nodes` | function | Parses Java file and asserts at least one node is returned |
| `tests/test_ast_parser.py::test_java_class_node` | function | Parses Java file and asserts existence of a class node |
| `tests/test_ast_parser.py::test_java_method_node` | function | Parses Java file and asserts existence of a method node |
| `tests/test_ast_parser.py::test_java_interface_node` | function | Parses Java file and asserts existence of an interface node |
| `tests/test_ast_parser.py::test_java_enum_node` | function | Parses Java file and asserts existence of an enum node |
| `tests/test_ast_parser.py::test_java_javadoc_extracted` | function | Parses Java file and verifies docstring extracted from javadoc |
| `tests/test_ast_parser.py::test_java_imports_extracted` | function | Parses Java file and verifies imports are extracted as Import nodes |
| `tests/test_ast_parser.py::test_ruby_parse_returns_nodes` | function | Parses Ruby file and asserts at least one node is returned |
| `tests/test_ast_parser.py::test_ruby_class_node` | function | Parses Ruby file and asserts existence of a class node |
| `tests/test_ast_parser.py::test_ruby_method_node` | function | Parses Ruby file and asserts existence of a method node |
| `tests/test_ast_parser.py::test_ruby_module_node` | function | Parses Ruby file and asserts existence of a module node |
| `tests/test_ast_parser.py::test_ruby_function_node` | function | Parses Ruby file and asserts existence of a function node |
| `tests/test_ast_parser.py::test_ruby_docstring_extracted` | function | Parses Ruby file and verifies docstring extracted from comments |
| `tests/test_config.py::_clean_env` | function | Removes predefined environment variables from os.environ |
| `tests/test_config.py::_restore_env` | function | Restores previously saved environment variables to os.environ |
| `tests/test_config.py::test_load_defaults` | function | Verifies load_config uses defaults when no config file found |
| `tests/test_config.py::test_save_and_reload` | function | Verifies config saved to file can be reloaded identically |
| `tests/test_config.py::test_partial_toml_uses_defaults` | function | Verifies partial TOML config merges with defaults |
| `tests/test_grouper.py::test_sparse_folders_merge_to_parent` | function | Asserts sparse folders merge into parent groups |
| `tests/test_grouper.py::test_dense_folder_gets_own_page` | function | Asserts dense folder with many files gets its own page |
| `tests/test_grouper.py::test_different_folders_get_separate_groups` | function | Asserts different folders are placed in separate groups |
| `tests/test_grouper.py::test_deep_sparse_merges_upward` | function | Asserts deep sparse folders merge upward to parent |
| `tests/test_grouper.py::test_root_level_files` | function | Asserts root-level files are assigned to the root group |
| `tests/test_grouper.py::test_returns_all_files` | function | Verifies density_group returns all input files in output |
| `tests/test_grouper.py::test_root_files_count_correctly` | function | Asserts root group file counts are computed correctly |
| `tests/test_manifest.py::test_compute_hash_stable` | function | Verifies compute_hash returns consistent hash for same content |
| `tests/test_manifest.py::test_empty_manifest_on_missing` | function | Verifies load_manifest returns empty dict when file missing |
| `tests/test_manifest.py::test_save_and_reload` | function | Verifies manifest can be saved to file and reloaded unchanged |
| `tests/test_manifest.py::test_stale_files_detected` | function | Identifies files with modified content as stale |
| `tests/test_manifest.py::test_fresh_file_not_stale` | function | Verifies files with matching hash are not marked stale |
| `tests/test_manifest.py::test_load_manifest_missing_component_ids` | function | Verifies load_manifest handles missing component_ids gracefully |
| `tests/test_wiki.py::_make_node` | function | Creates an ASTNode instance with given or default attributes for testing |
| `tests/test_wiki.py::test_build_page_contains_symbol` | function | Verifies built page contains the symbol name |
| `tests/test_wiki.py::test_build_page_contains_calls` | function | Verifies built page includes calls from the symbol |
| `tests/test_wiki.py::test_build_page_contains_called_by` | function | Verifies built page includes called_by references |
| `tests/test_wiki.py::test_build_page_no_agent_hints` | function | Verifies built page does not contain agent hint strings |
| `tests/test_wiki.py::test_build_index_contains_page` | function | Verifies build_index includes entry for the provided page |
| `tests/test_wiki.py::test_write_page_creates_file` | function | Verifies write_page creates the file with correct content |
## Data Flows
- client calls parse_file(path) → language‑specific backend returns raw CST → converter transforms to uniform Node list → list is cached and returned
- parse_file → Node list → grouper.group(nodes) → returns hierarchy (class→methods, module→functions)
- parse_file → Node list → wiki.generate_docs(nodes) → writes markdown for each symbol’s docstring
- parse_file → Node list → manifest.build_manifest(nodes) → produces mapping of file to symbol metadata
## Design Constraints
- Cached nodes are stored as pickled files keyed by file path; cache is invalidated only on file modification time, not content hash, so timestamps must be reliable across runs.
- Docstring extraction differs per language: Java parses Javadoc comments, Python uses docstring statements, Ruby and Rust use doc comments (///, /**). The parser must strip leading `*` and whitespace uniformly.
- Rust trait methods are emitted as separate `Node` objects with type `trait_method` and a parent reference to the trait node; they are not nested inside the trait's method list.
- Imports are always emitted as synthetic `Node` objects of type `Import`; they do not carry docstrings or calls, only a `name` field (the fully qualified import path) and a `line` number.
- Java enums and interfaces are parsed as `class` nodes with a `kind` field set to `enum` or `interface`; the same unified `Node` structure is used, not separate subtypes.
- Ruby module nodes are top‑level constructs; inside them, classes and methods are nested by line‑range rather than as child references — consumers must flatten manually if needed.
## Relationships
- **Calls:** ASTNode, Config, FileEntry, IndexEntry, Manifest, NamedTemporaryFile, PageContext, Path, TemporaryDirectory, _clean_env, _make_node, _restore_env, all, any, build_index, build_page, compute_hash, density_group, dict, dumps, endswith, exists, isinstance, items, keys, len, load_cached_nodes, load_config, load_manifest, lower, mkdir, next, parse_file, pop, range, read_text, save_cached_nodes, save_config, save_manifest, set, stale_files, startswith, update, values, write, write_bytes, write_page, write_text
- **Called by:** tests/test_config.py::test_load_defaults, tests/test_config.py::test_partial_toml_uses_defaults, tests/test_config.py::test_save_and_reload, tests/test_wiki.py::test_build_page_contains_called_by, tests/test_wiki.py::test_build_page_contains_calls, tests/test_wiki.py::test_build_page_contains_symbol, tests/test_wiki.py::test_build_page_no_agent_hints, tests/test_wiki.py::test_write_page_creates_file
- **Imports from:** indexer.ast_parser.ASTNode, indexer.ast_parser.compute_hash_short, indexer.ast_parser.load_cached_nodes, indexer.ast_parser.parse_file, indexer.ast_parser.save_cached_nodes, indexer.config.Config, indexer.config.load_config, indexer.config.save_config, indexer.grouper.density_group, indexer.manifest.FileEntry, indexer.manifest.Manifest, indexer.manifest.compute_hash, indexer.manifest.load_manifest, indexer.manifest.save_manifest, indexer.utils, indexer.wiki.IndexEntry, indexer.wiki.PageContext, indexer.wiki.build_index, indexer.wiki.build_page, indexer.wiki.write_page, json, os, pathlib.Path, tempfile
## Entry Points
- `test_parse_returns_nodes`
- `test_function_node`
- `test_method_node`
- `test_class_node`
- `test_docstring_extracted`
- `test_imports_extracted`
- `test_calls_extracted`
- `test_cache_roundtrip`
- `test_rust_parse_returns_nodes`
- `test_rust_function_node`
- `test_rust_struct_node`
- `test_rust_method_node`
- `test_rust_trait_node`
- `test_rust_trait_method_spec`
- `test_rust_enum_node`
- `test_rust_type_alias`
- `test_rust_docstring_extracted`
- `test_rust_imports_extracted`
- `test_java_parse_returns_nodes`
- `test_java_class_node`
- `test_java_method_node`
- `test_java_interface_node`
- `test_java_enum_node`
- `test_java_javadoc_extracted`
- `test_java_imports_extracted`
- `test_ruby_parse_returns_nodes`
- `test_ruby_class_node`
- `test_ruby_method_node`
- `test_ruby_module_node`
- `test_ruby_function_node`
- `test_ruby_docstring_extracted`
- `test_load_defaults`
- `test_save_and_reload`
- `test_partial_toml_uses_defaults`
- `test_sparse_folders_merge_to_parent`
- `test_dense_folder_gets_own_page`
- `test_different_folders_get_separate_groups`
- `test_deep_sparse_merges_upward`
- `test_root_level_files`
- `test_returns_all_files`
- `test_root_files_count_correctly`
- `test_compute_hash_stable`
- `test_empty_manifest_on_missing`
- `test_save_and_reload`
- `test_stale_files_detected`
- `test_fresh_file_not_stale`
- `test_load_manifest_missing_component_ids`
- `test_build_page_contains_symbol`
- `test_build_page_contains_calls`
- `test_build_page_contains_called_by`
- `test_build_page_no_agent_hints`
- `test_build_index_contains_page`
- `test_write_page_creates_file`
