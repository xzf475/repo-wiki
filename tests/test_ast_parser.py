import tempfile, json
from pathlib import Path
from indexer.ast_parser import parse_file, ASTNode, compute_hash_short, load_cached_nodes, save_cached_nodes

FIXTURE = Path(__file__).parent / "fixtures/sample_py/auth.py"
RUST_FIXTURE = Path(__file__).parent / "fixtures/sample_rust/lib.rs"
JAVA_FIXTURE = Path(__file__).parent / "fixtures/sample_java/App.java"
RUBY_FIXTURE = Path(__file__).parent / "fixtures/sample_ruby/app.rb"

def test_parse_returns_nodes():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    assert len(nodes) > 0

def test_function_node():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("require_auth" in i for i in ids)

def test_method_node():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("TokenValidator.refresh" in i for i in ids)

def test_class_node():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::TokenValidator") for i in ids)

def test_docstring_extracted():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    method = next(n for n in nodes if "TokenValidator.refresh" in n.id)
    assert method.docstring is not None
    assert "OAuth2" in method.docstring

def test_imports_extracted():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    # imports are file-level; all nodes from this file should carry them
    method = next(n for n in nodes if "TokenValidator.refresh" in n.id)
    assert isinstance(method.imports, list)
    assert len(method.imports) > 0

def test_calls_extracted():
    nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
    method = next(n for n in nodes if "TokenValidator.refresh" in n.id)
    assert "sign_payload" in method.calls

def test_cache_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        nodes = parse_file(FIXTURE, repo_root=FIXTURE.parent.parent.parent)
        file_hash = "abc123"
        save_cached_nodes(root, file_hash, nodes)
        loaded = load_cached_nodes(root, file_hash)
        assert loaded is not None
        assert len(loaded) == len(nodes)
        assert loaded[0].id == nodes[0].id

# ── Rust ──────────────────────────────────────────────────────────────────────

def test_rust_parse_returns_nodes():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    assert len(nodes) > 0

def test_rust_function_node():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("age_difference" in i for i in ids)

def test_rust_struct_node():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::User") for i in ids)

def test_rust_method_node():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("User.new" in i for i in ids)
    assert any("User.is_adult" in i for i in ids)

def test_rust_trait_node():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::ToJson") for i in ids)

def test_rust_trait_method_spec():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("ToJson.to_json" in i for i in ids)

def test_rust_enum_node():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::Status") for i in ids)

def test_rust_type_alias():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::UserResult") for i in ids)

def test_rust_docstring_extracted():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    func = next(n for n in nodes if "age_difference" in n.id)
    assert func.docstring is not None
    assert "age difference" in func.docstring

def test_rust_imports_extracted():
    nodes = parse_file(RUST_FIXTURE, repo_root=RUST_FIXTURE.parent.parent.parent)
    func = next(n for n in nodes if "age_difference" in n.id)
    assert isinstance(func.imports, list)
    assert len(func.imports) > 0

# ── Java ──────────────────────────────────────────────────────────────────────

def test_java_parse_returns_nodes():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    assert len(nodes) > 0

def test_java_class_node():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::App") for i in ids)

def test_java_method_node():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("App.addUser" in i for i in ids)
    assert any("App.getUserCount" in i for i in ids)

def test_java_interface_node():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::UserProfile") for i in ids)

def test_java_enum_node():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::Role") for i in ids)

def test_java_javadoc_extracted():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    cls = next(n for n in nodes if n.id.endswith("::App"))
    assert cls.docstring is not None
    assert "application class" in cls.docstring

    method = next(n for n in nodes if "App.addUser" in n.id)
    assert method.docstring is not None
    assert "Adds a user" in method.docstring

def test_java_imports_extracted():
    nodes = parse_file(JAVA_FIXTURE, repo_root=JAVA_FIXTURE.parent.parent.parent)
    cls = next(n for n in nodes if n.id.endswith("::App"))
    assert isinstance(cls.imports, list)
    assert len(cls.imports) > 0

# ── Ruby ──────────────────────────────────────────────────────────────────────

def test_ruby_parse_returns_nodes():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    assert len(nodes) > 0

def test_ruby_class_node():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::Router") for i in ids)

def test_ruby_method_node():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any("Router.initialize" in i for i in ids)
    assert any("Router.add_route" in i for i in ids)
    assert any("Router.dispatch" in i for i in ids)

def test_ruby_module_node():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::Parser") for i in ids)

def test_ruby_function_node():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    ids = [n.id for n in nodes]
    assert any(i.endswith("::parse") for i in ids)

def test_ruby_docstring_extracted():
    nodes = parse_file(RUBY_FIXTURE, repo_root=RUBY_FIXTURE.parent.parent.parent)
    cls = next(n for n in nodes if n.id.endswith("::Router"))
    assert cls.docstring is not None
    assert "routing" in cls.docstring.lower()
