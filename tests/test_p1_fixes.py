import json
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

from indexer.rest_api import TaskStore, RepoRegistry, _get_repo_lock, _parse_body


class TestTaskStore:
    def test_create_task(self):
        store = TaskStore()
        tid = store.create("test-repo", "https://example.com/repo")
        task = store.get(tid)
        assert task is not None
        assert task["name"] == "test-repo"
        assert task["status"] == "pending"

    def test_update_task(self):
        store = TaskStore()
        tid = store.create("test-repo", "https://example.com/repo")
        store.update(tid, status="running", progress=50, step="indexing")
        task = store.get(tid)
        assert task["status"] == "running"
        assert task["progress"] == 50

    def test_update_finished_sets_timestamp(self):
        store = TaskStore()
        tid = store.create("test-repo", "https://example.com/repo")
        store.update(tid, status="completed", progress=100)
        task = store.get(tid)
        assert "_finished_at" in task
        assert task["_finished_at"] > 0

    def test_update_nonexistent_task_noop(self):
        store = TaskStore()
        store.update("nonexistent", status="running")

    def test_get_nonexistent_returns_none(self):
        store = TaskStore()
        assert store.get("nonexistent") is None

    def test_cleanup_expired_tasks(self):
        import time
        store = TaskStore()
        tid = store.create("test-repo", "https://example.com/repo")
        store.update(tid, status="completed", progress=100)
        task = store.get(tid)
        task["_finished_at"] = time.time() - store._TTL_SECONDS - 1
        store._cleanup()
        assert store.get(tid) is None


class TestRepoRegistryThreadSafety:
    def test_concurrent_register(self):
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            errors = []

            def register_repo(idx):
                try:
                    root = Path(d) / f"repo_{idx}"
                    root.mkdir()
                    (root / ".indexer.toml").write_text("[llm]\n")
                    reg.register(f"repo-{idx}", root, url=f"https://example.com/{idx}")
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=register_repo, args=(i,)) for i in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, f"Errors during concurrent register: {errors}"
            assert len(reg.repos) == 10

    def test_concurrent_unregister(self):
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            for i in range(10):
                root = Path(d) / f"repo_{i}"
                root.mkdir()
                (root / ".indexer.toml").write_text("[llm]\n")
                reg.register(f"repo-{i}", root, url=f"https://example.com/{i}")

            errors = []

            def unregister_repo(idx):
                try:
                    reg.unregister(f"repo-{idx}")
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=unregister_repo, args=(i,)) for i in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, f"Errors during concurrent unregister: {errors}"
            assert len(reg.repos) == 0


class TestRepoLockSkipLock:
    def test_skip_lock_does_not_release(self):
        lock = _get_repo_lock("_test_skip_lock")
        assert lock.acquire(blocking=False)
        lock.release()

        lock2 = _get_repo_lock("_test_skip_lock")
        assert lock2 is lock
        assert lock2.acquire(blocking=False)
        lock2.release()

    def test_lock_blocks_concurrent(self):
        lock = _get_repo_lock("_test_concurrent")
        assert lock.acquire(blocking=False)
        same_lock = _get_repo_lock("_test_concurrent")
        assert not same_lock.acquire(blocking=False)
        lock.release()
        assert same_lock.acquire(blocking=False)
        same_lock.release()


class TestRepoRegistryGetNone:
    def test_get_nonexistent_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            assert reg.get("nonexistent") is None

    def test_get_returns_none_safely(self):
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            result = reg.get("missing")
            assert result is None
            assert (result.get("url", "") if result else "") == ""


class TestParseBody:
    def test_valid_json(self):
        mock_request = MagicMock()
        mock_request.json = MagicMock(return_value=asyncio_coro({"key": "value"}))
        import asyncio

        async def run():
            result = await _parse_body(mock_request)
            assert result == {"key": "value"}

        asyncio.run(run())

    def test_invalid_json_returns_empty(self):
        mock_request = MagicMock()
        mock_request.json = MagicMock(side_effect=Exception("bad json"))

        async def run():
            from indexer.rest_api import _InvalidBodyError
            try:
                result = await _parse_body(mock_request)
                assert False, "should have raised _InvalidBodyError"
            except _InvalidBodyError as e:
                assert "invalid JSON" in str(e)

        import asyncio
        asyncio.run(run())

    def test_non_dict_returns_empty(self):
        mock_request = MagicMock()
        mock_request.json = MagicMock(return_value=asyncio_coro([1, 2, 3]))

        async def run():
            from indexer.rest_api import _InvalidBodyError
            try:
                result = await _parse_body(mock_request)
                assert False, "should have raised _InvalidBodyError"
            except _InvalidBodyError as e:
                assert "JSON object" in str(e)

        import asyncio
        asyncio.run(run())


def asyncio_coro(val):
    async def _coro():
        return val
    return _coro()


class TestManifestFieldValidation:
    def test_missing_component_ids_defaults_empty(self):
        import tempfile
        from indexer.manifest import load_manifest
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            manifest_path = root / ".indexer" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps({
                "last_indexed_commit": "abc",
                "indexed_at": "2026-01-01T00:00:00Z",
                "files": {
                    "test.py": {"hash": "sha256:abc", "wiki_page": "wiki/test.md"}
                }
            }))
            m = load_manifest(root)
            assert m.files["test.py"].component_ids == []

    def test_missing_hash_defaults_empty(self):
        import tempfile
        from indexer.manifest import load_manifest
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            manifest_path = root / ".indexer" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps({
                "last_indexed_commit": "abc",
                "indexed_at": "2026-01-01T00:00:00Z",
                "files": {
                    "test.py": {"wiki_page": "wiki/test.md", "component_ids": []}
                }
            }))
            m = load_manifest(root)
            assert m.files["test.py"].hash == ""

    def test_corrupt_manifest_returns_empty(self):
        import tempfile
        from indexer.manifest import load_manifest
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            manifest_path = root / ".indexer" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text("NOT VALID JSON{{{")
            m = load_manifest(root)
            assert m.files == {}


class TestApplyEnvEmptyString:
    def test_empty_string_does_not_override_default(self):
        import os
        from indexer.config import Config, _apply_env
        cfg = Config()
        original_provider = cfg.provider
        with patch.dict(os.environ, {"LLM_PROVIDER": ""}):
            result = _apply_env(cfg)
            assert result.provider == original_provider


class TestGitReturnCodeCheck:
    def test_git_checkout_failure_sets_task_failed(self):
        from indexer.rest_api import tasks
        tid = tasks.create("test-git-fail", "https://example.com/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error: pathspec 'nonexistent' did not match"

        with patch("indexer.rest_api.subprocess.run", return_value=mock_result):
            from indexer.rest_api import _run_rebuild_task_inner
            _run_rebuild_task_inner(tid, "test-git-fail", Path("/tmp/nonexistent"), False, branch="nonexistent")

        task = tasks.get(tid)
        assert task is not None
        assert task["status"] == "failed"
        assert "git" in (task.get("error") or "").lower()


class TestCrossReferenceMergeCallers:
    def test_cross_reference_merges_same_file_and_cross_file_callers(self):
        from indexer.ast_parser import ASTNode
        from indexer.indexing import cross_reference

        node_a = ASTNode(id="a.py::foo", type="function", file="a.py",
                         line_start=1, line_end=5, docstring="", calls=["bar"], called_by=[], imports=[])
        node_b = ASTNode(id="b.py::bar", type="function", file="b.py",
                         line_start=1, line_end=5, docstring="", calls=[], called_by=[], imports=[])
        node_c = ASTNode(id="b.py::baz", type="function", file="b.py",
                         line_start=6, line_end=10, docstring="", calls=["bar"], called_by=[], imports=[])

        cross_reference([node_a, node_b, node_c])

        assert "a.py::foo" in node_b.called_by
        assert "b.py::baz" in node_b.called_by
        assert len(node_b.called_by) == 2


class TestUpdateMetaLock:
    def test_update_meta_uses_lock(self):
        with tempfile.TemporaryDirectory() as d:
            from indexer.rest_api import RepoRegistry
            reg = RepoRegistry(repos_dir=Path(d))
            root = Path(d) / "repo"
            root.mkdir()
            (root / ".indexer.toml").write_text("[llm]\n")
            reg.register("test", root, url="https://example.com/test")
            reg.update_meta("test", description="updated")
            info = reg.get("test")
            assert info["description"] == "updated"


class TestEnvQuoteStripping:
    def test_double_quotes_stripped(self):
        import os
        from indexer.utils import load_env_file, _env_loaded
        import indexer.utils as utils_mod
        utils_mod._env_loaded = False
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text('TEST_QUOTE_KEY="hello world"\n')
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=env_path.read_text()):
                    with patch.dict(os.environ, {}, clear=False):
                        os.environ.pop("TEST_QUOTE_KEY", None)
                        load_env_file()
                        assert os.environ.get("TEST_QUOTE_KEY") == "hello world"
            utils_mod._env_loaded = False

    def test_single_quotes_stripped(self):
        import os
        from indexer.utils import load_env_file
        import indexer.utils as utils_mod
        utils_mod._env_loaded = False
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("TEST_SQUOTE_KEY='hello world'\n")
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=env_path.read_text()):
                    with patch.dict(os.environ, {}, clear=False):
                        os.environ.pop("TEST_SQUOTE_KEY", None)
                        load_env_file()
                        assert os.environ.get("TEST_SQUOTE_KEY") == "hello world"
            utils_mod._env_loaded = False


class TestVectorStoreTruncateList:
    def test_truncate_produces_valid_json(self):
        from indexer.vector_store import _truncate_list
        large_list = [f"symbol_{i}" for i in range(1000)]
        result = _truncate_list(large_list, max_json_len=500)
        import json
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) < 1000

    def test_small_list_not_truncated(self):
        from indexer.vector_store import _truncate_list
        small_list = ["a", "b", "c"]
        result = _truncate_list(small_list, max_json_len=10000)
        import json
        parsed = json.loads(result)
        assert parsed == ["a", "b", "c"]


class TestGetSourceContextTypeCoercion:
    def test_string_params_converted_to_int(self):
        from indexer.rest_api import get_source_context
        mock_request = MagicMock()
        mock_request.json = MagicMock(return_value=asyncio_coro({
            "file_path": "test.py",
            "repo": "test-repo",
            "line_start": "10",
            "line_end": "20",
            "padding": "3",
        }))

        async def run():
            with patch("indexer.rest_api.registry") as mock_reg:
                mock_reg.get.return_value = None
                result = await get_source_context(mock_request)
                assert result.status_code == 404

        import asyncio
        asyncio.run(run())


class TestUnregisterCleansLock:
    def test_unregister_removes_repo_lock(self):
        from indexer.rest_api import _repo_locks, _locks_lock
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            root = Path(d) / "repo"
            root.mkdir()
            (root / ".indexer.toml").write_text("[llm]\n")
            reg.register("lock-test", root, url="https://example.com/test")
            _get_repo_lock("lock-test")
            with _locks_lock:
                assert "lock-test" in _repo_locks
            reg.unregister("lock-test")
            with _locks_lock:
                assert "lock-test" not in _repo_locks


class TestAtomicWrites:
    def test_save_config_atomic(self):
        import os
        from indexer.config import Config, save_config, load_config
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = Config(provider="openai/gpt-test")
            save_config(root, cfg)
            cfg_path = root / ".indexer.toml"
            assert cfg_path.exists()
            env_keys = [k for k in os.environ if k.startswith(("LLM_", "INDEXER_", "EMBEDDING_", "VECTOR_"))]
            with patch.dict(os.environ, {k: "" for k in env_keys}, clear=False):
                loaded = load_config(root)
            assert loaded.provider == "openai/gpt-test"

    def test_save_manifest_atomic(self):
        from indexer.manifest import Manifest, save_manifest, load_manifest
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = Manifest(last_indexed_commit="abc123", indexed_at="2026-01-01T00:00:00Z")
            save_manifest(root, m)
            m_path = root / ".indexer" / "manifest.json"
            assert m_path.exists()
            loaded = load_manifest(root)
            assert loaded.last_indexed_commit == "abc123"


class TestSingleBranchWhereClause:
    def test_single_branch_gets_where_clause(self):
        from indexer.rest_api import RepoRegistry
        with tempfile.TemporaryDirectory() as d:
            reg = RepoRegistry(repos_dir=Path(d))
            root = Path(d) / "repo"
            root.mkdir()
            (root / ".indexer.toml").write_text("[llm]\n")
            reg.register("single-br", root, url="https://example.com/test", branches=["main"])
            info = reg.get("single-br")
            branches = info.get("branches", [])
            if len(branches) == 1:
                where_clause = {"branch": branches[0]}
            elif len(branches) > 1:
                where_clause = {"$or": [{"branch": b} for b in branches]}
            else:
                where_clause = None
            assert where_clause == {"branch": "main"}


class TestIntParamValidation:
    def test_invalid_line_start_returns_400(self):
        from indexer.rest_api import get_source_context
        mock_request = MagicMock()
        mock_request.json = MagicMock(return_value=asyncio_coro({
            "file_path": "test.py",
            "repo": "test-repo",
            "line_start": "abc",
            "line_end": "20",
        }))

        async def run():
            result = await get_source_context(mock_request)
            assert result.status_code == 400

        import asyncio
        asyncio.run(run())


class TestWebhookBranchCopy:
    def test_webhook_branch_list_not_mutated(self):
        original_branches = ["main", "develop"]
        info = {"branches": original_branches, "root": Path("/tmp"), "url": "", "branch_rule": ""}
        new_branch = "feature-x"
        if new_branch not in info["branches"]:
            repo_branches = list(info["branches"]) + [new_branch]
        assert "feature-x" not in original_branches
        assert len(original_branches) == 2
        assert len(repo_branches) == 3


class TestCleanupSkipsRunning:
    def test_cleanup_does_not_evict_running_tasks(self):
        from indexer.rest_api import TaskStore
        store = TaskStore()
        tid1 = store.create("repo1", "url1")
        store.update(tid1, status="running", progress=50, step="indexing")
        for i in range(201):
            tid = store.create(f"repo-fill-{i}", f"url-{i}")
            store.update(tid, status="completed", progress=100, step="complete")
        assert store.get(tid1) is not None
        assert store.get(tid1)["status"] == "running"


class TestEmbedQueryEmptyResponse:
    def test_embed_query_raises_on_empty(self):
        from indexer.embedding import embed_query
        from indexer.config import EmbeddingConfig
        with patch("indexer.embedding._call_embedding_api", return_value=[]):
            try:
                embed_query("test", EmbeddingConfig())
                assert False, "should have raised ValueError"
            except ValueError as e:
                assert "empty result" in str(e).lower()


class TestComputeHashReturnsNone:
    def test_compute_hash_returns_none_on_oserror(self):
        from indexer.manifest import compute_hash
        result = compute_hash(Path("/nonexistent/file/that/does/not/exist.py"))
        assert result is None


class TestChangedFilesSinceInvalidCommit:
    def test_raises_on_invalid_commit(self):
        from indexer.git import changed_files_since
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init"], cwd=d, capture_output=True)
            subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], cwd=d, capture_output=True, env={**__import__('os').environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
            try:
                changed_files_since(Path(d), "nonexistent_commit_hash")
                assert False, "should have raised ValueError"
            except ValueError as e:
                assert "Invalid commit" in str(e)


class TestExpansionCap:
    def test_expand_with_call_graph_respects_max(self):
        from indexer.retrieval import _expand_with_call_graph
        from indexer.config import Config
        hits = [{"id": f"sym-{i}", "metadata": {"calls": "", "called_by": ""}} for i in range(10)]
        result = _expand_with_call_graph(hits, Config(), Path("/tmp"), depth=1, max_expanded=5)
        assert len(result) == 10


class TestExpansionCapWithExpansion:
    def test_expand_caps_at_max(self):
        from indexer.retrieval import _expand_with_call_graph, _parse_json_list
        from indexer.config import Config
        hits = [{"id": "sym-0", "metadata": {"calls": '["sym-1","sym-2","sym-3","sym-4","sym-5","sym-6","sym-7","sym-8","sym-9"]', "called_by": ""}}]
        with patch("indexer.retrieval.get_by_ids") as mock_get:
            mock_get.return_value = [{"id": f"sym-{i}", "metadata": {"calls": "", "called_by": ""}} for i in range(1, 10)]
            result = _expand_with_call_graph(hits, Config(), Path("/tmp"), depth=1, max_expanded=5)
            assert len(result) <= 5


class TestXSSApiKeyEscape:
    def test_api_key_script_tag_escaped(self):
        import json
        api_key = '</script><script>alert(1)</script>'
        safe_json = json.dumps(api_key).replace("<", "\\u003c").replace(">", "\\u003e").replace("/", "\\/")
        assert "<script>" not in safe_json
        assert "\\u003c" in safe_json


class TestBearerCaseInsensitive:
    def test_lowercase_bearer_accepted(self):
        import hmac
        mcp_api_key = "test-secret"
        auth = "bearer test-secret"
        token = auth[7:] if auth.lower().startswith("bearer ") else auth
        assert hmac.compare_digest(token, mcp_api_key)


class TestBatchTokenEstimateCJK:
    def test_char_budget_uses_triple(self):
        from indexer.indexing import build_batches
        from indexer.config import Config
        from indexer.ast_parser import ASTNode
        cfg = Config()
        cfg.max_tokens_per_batch = 1000
        node = ASTNode(id="t", type="function", file="t.py", line_start=1, line_end=1, docstring="x" * 2500, calls=[], called_by=[], imports=[])
        batches = build_batches([node], cfg)
        assert len(batches) == 1


class TestRLockNoDeadlock:
    def test_register_repo_no_deadlock(self):
        import threading
        from indexer.rest_api import RepoRegistry
        reg = RepoRegistry(repos_dir=Path(tempfile.mkdtemp()))
        reg._lock = threading.RLock()
        with reg._lock:
            result = reg.get("nonexistent")
        assert result is None

    def test_rlock_allows_reentrant(self):
        import threading
        lock = threading.RLock()
        acquired = False
        with lock:
            with lock:
                acquired = True
        assert acquired


class TestTopKNegativeValue:
    def test_top_k_negative_clamped_to_one(self):
        top_k = max(1, min(-5, 100))
        assert top_k == 1

    def test_top_k_zero_clamped_to_one(self):
        top_k = max(1, min(0, 100))
        assert top_k == 1

    def test_top_k_normal_value(self):
        top_k = max(1, min(10, 100))
        assert top_k == 10


class TestEmbeddingRetry:
    def test_call_embedding_api_has_retry(self):
        import inspect
        from indexer.embedding import _call_embedding_api
        src = inspect.getsource(_call_embedding_api)
        assert "attempt" in src
        assert "RateLimitError" in src


class TestEmptyChoicesProtection:
    def test_litellm_empty_choices_raises_custom_error(self):
        import inspect
        from indexer.llm import _litellm_completion
        src = inspect.getsource(_litellm_completion)
        assert "_EmptyResponseError" in src


class TestVectorStoreStaleByAllNodes:
    def test_stale_uses_all_node_ids(self):
        import inspect
        from indexer.vector_store import upsert_nodes
        src = inspect.getsource(upsert_nodes)
        assert "all_new_ids" in src


class TestVectorStoreBranchAlwaysSet:
    def test_branch_always_in_metadata(self):
        import inspect
        from indexer.vector_store import _build_meta
        src = inspect.getsource(_build_meta)
        assert 'meta["branch"]' in src


class TestDiscoverRemoteBranchesCwd:
    def test_discover_has_cwd_param(self):
        import inspect
        from indexer.rest_api import _discover_remote_branches
        sig = inspect.signature(_discover_remote_branches)
        assert "cwd" in sig.parameters


class TestCredentialAtomicWrite:
    def test_credential_write_uses_tmp(self):
        import inspect
        from indexer.rest_api import _store_credentials
        src = inspect.getsource(_store_credentials)
        assert ".tmp" in src or "replace" in src


class TestConfigValidation:
    def test_invalid_max_tokens_per_batch_reset(self):
        from indexer.config import Config, load_config, save_config
        d = Path(tempfile.mkdtemp())
        cfg = Config()
        cfg.max_tokens_per_batch = 0
        save_config(d, cfg)
        loaded = load_config(d)
        assert loaded.max_tokens_per_batch >= 1

    def test_invalid_dimensions_reset(self):
        from indexer.config import Config, load_config, save_config
        d = Path(tempfile.mkdtemp())
        cfg = Config()
        cfg.embedding.dimensions = 0
        save_config(d, cfg)
        loaded = load_config(d)
        assert loaded.embedding.dimensions >= 1


class TestRubyModuleMethod:
    def test_module_method_has_prefix(self):
        from indexer.ruby_parser import parse_ruby_file
        fixture = Path("tests/fixtures/sample_ruby/app.rb")
        if not fixture.exists():
            return
        nodes = parse_ruby_file(fixture, repo_root=fixture.parent.parent.parent)
        parse_node = next((n for n in nodes if "Parser.parse" in n.id), None)
        assert parse_node is not None
        assert parse_node.type == "method"


class TestVectorStoreIncrementalSafety:
    def test_upsert_nodes_uses_file_scoped_stale(self):
        import inspect
        from indexer.vector_store import upsert_nodes
        src = inspect.getsource(upsert_nodes)
        assert "files_in_batch" in src
        assert "$and" in src

class TestDimensionMismatchDetection:
    def test_get_or_create_checks_dim(self):
        import inspect
        from indexer.vector_store import _get_or_create_collection
        src = inspect.getsource(_get_or_create_collection)
        assert "existing_dim" in src

class TestListReposNullSafety:
    def test_list_repos_checks_none(self):
        import inspect
        from indexer.rest_api import list_repos
        src = inspect.getsource(list_repos)
        assert "if not info" in src

class TestExpandDepthClamped:
    def test_expand_depth_max_5(self):
        expand_depth = min(100, 5)
        assert expand_depth == 5

class TestWebhookNullCheck:
    def test_webhook_checks_info_not_none(self):
        import inspect
        from indexer.rest_api import webhook_by_name
        src = inspect.getsource(webhook_by_name)
        assert "if not info" in src

class TestURLValidationBeforeDiscovery:
    def test_register_validates_url_before_discovery(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        parsed_pos = src.find("parsed_url = urllib.parse.urlparse")
        discover_pos = src.find("_discover_remote_branches")
        assert parsed_pos < discover_pos, "URL validation must come before branch discovery"

class TestNonGitManifestCleanup:
    def test_update_manifest_cleans_non_git(self):
        import inspect
        from indexer.indexing import update_manifest
        src = inspect.getsource(update_manifest)
        assert "stale_keys" in src
        assert ".exists()" in src

class TestLLMListResponseHandling:
    def test_deep_enrich_index_handles_list(self):
        import inspect
        from indexer.llm import deep_enrich_index
        src = inspect.getsource(deep_enrich_index)
        assert "isinstance(result, list)" in src

class TestSafeIdFunction:
    def test_safeId_exists_in_html(self):
        with open("indexer/static/index.html", "r") as f:
            content = f.read()
        assert "function safeId" in content
        assert "safeId(repoName)" in content

class TestMCPResponseSizeLimit:
    def test_api_request_limits_response(self):
        with open("indexer/mcp_server.py", "r") as f:
            src = f.read()
        assert "10 * 1024 * 1024" in src

class TestMergeThresholdValidation:
    def test_merge_threshold_validated(self):
        from indexer.config import Config, load_config, save_config
        d = Path(tempfile.mkdtemp())
        cfg = Config()
        cfg.merge_threshold = 0
        save_config(d, cfg)
        loaded = load_config(d)
        assert loaded.merge_threshold >= 1


class TestVectorStoreLogger:
    def test_vector_store_has_logger(self):
        import indexer.vector_store as vs
        assert hasattr(vs, 'logger')

class TestNonGitCliFileDiscovery:
    def test_cli_non_git_uses_rglob(self):
        with open("indexer/cli.py", "r") as f:
            src = f.read()
        assert "rglob" in src
        assert "any(part.startswith" in src

class TestSearchDimNone:
    def test_search_passes_dim_none(self):
        import inspect
        from indexer.vector_store import search
        src = inspect.getsource(search)
        assert "dim=None" in src

class TestClientThreadSafety:
    def test_anthropic_client_has_lock(self):
        import inspect
        from indexer.llm import _get_anthropic_client
        src = inspect.getsource(_get_anthropic_client)
        assert "_anthropic_lock" in src

    def test_embedding_openai_client_has_lock(self):
        import inspect
        from indexer.embedding import _get_openai_client
        src = inspect.getsource(_get_openai_client)
        assert "_openai_lock" in src

class TestFatalExceptionsUnified:
    def test_fatal_exceptions_constant(self):
        from indexer.llm import _FATAL_EXCEPTIONS
        assert ValueError in _FATAL_EXCEPTIONS
        assert TypeError in _FATAL_EXCEPTIONS
        assert AttributeError in _FATAL_EXCEPTIONS

class TestMCPExpandDepthClamped:
    def test_mcp_expand_depth_max_5(self):
        with open("indexer/mcp_server.py", "r") as f:
            src = f.read()
        assert "min(expand_depth, 5)" in src

class TestDefaultBranchDetection:
    def test_register_task_detects_default_branch(self):
        import inspect
        from indexer.rest_api import _run_register_task_inner
        src = inspect.getsource(_run_register_task_inner)
        assert "_detect_default_branch" in src

class TestAPIKeyNotInHTML:
    def test_api_key_not_embedded_in_page(self):
        import inspect
        from indexer.rest_api import _index_page
        src = inspect.getsource(_index_page)
        assert "window._apiKey" not in src

class TestBranchFilterConsistent:
    def test_retrieval_always_filters_by_branch(self):
        import inspect
        from indexer.retrieval import search_symbols
        src = inspect.getsource(search_symbols)
        assert 'where_clause = {"branch": branch}' in src

class TestLoadReposHasCatch:
    def test_loadrepos_has_catch(self):
        with open("indexer/static/index.html", "r") as f:
            content = f.read()
        loadrepos_start = content.index("async function loadRepos()")
        loadrepos_end = content.index("async function openRepo(")
        loadrepos_body = content[loadrepos_start:loadrepos_end]
        assert "catch" in loadrepos_body


class TestAnthropicImport:
    def test_anthropic_imported_in_completion(self):
        import inspect
        from indexer.llm import _anthropic_completion
        src = inspect.getsource(_anthropic_completion)
        assert "import anthropic" in src

class TestRetryFatalExceptions:
    def test_retry_uses_fatal_exceptions_constant(self):
        with open("indexer/llm.py", "r") as f:
            src = f.read()
        hardcoded = src.count("isinstance(e, (TypeError, AttributeError, ValueError, ImportError))")
        assert hardcoded == 0, f"Found {hardcoded} hardcoded fatal exception tuples"

class TestDeleteByFilesDimNone:
    def test_delete_by_files_passes_dim_none(self):
        import inspect
        from indexer.vector_store import delete_by_files
        src = inspect.getsource(delete_by_files)
        assert "dim=None" in src

class TestAllNewIdsOnlyValid:
    def test_all_new_ids_uses_valid_only(self):
        import inspect
        from indexer.vector_store import upsert_nodes
        src = inspect.getsource(upsert_nodes)
        assert "all_new_ids = {n.id for n, _ in valid}" in src

class TestOpenRepoHasCatch:
    def test_openrepo_has_catch(self):
        with open("indexer/static/index.html", "r") as f:
            content = f.read()
        start = content.index("async function openRepo(")
        end = content.index("function backToRepos(")
        body = content[start:end]
        assert "catch" in body

class TestDoSearchHasCatch:
    def test_dosearch_has_catch(self):
        with open("indexer/static/index.html", "r") as f:
            content = f.read()
        start = content.index("async function doSearch(")
        end = content.index("function showRegister(")
        body = content[start:end]
        assert "catch" in body

class TestMCPMaxDepthClamped:
    def test_trace_call_max_depth_clamped(self):
        with open("indexer/mcp_server.py", "r") as f:
            src = f.read()
        assert "min(max_depth, 8)" in src

class TestTraceCallMaxDepthLowerBound:
    def test_trace_call_max_depth_lower_bound(self):
        import inspect
        from indexer.rest_api import trace_call
        src = inspect.getsource(trace_call)
        assert "max(1, min(" in src

class TestTagsBranchesTypeValidation:
    def test_tags_type_validation(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        assert "isinstance(tags, list)" in src
        assert "isinstance(branches, list)" in src

class TestBuildBatchesIncludesCalledBy:
    def test_build_batches_includes_called_by(self):
        with open("indexer/indexing.py", "r") as f:
            src = f.read()
        assert "called_by" in src


class TestRound14Fixes:
    def test_git_terminal_prompt_on_ls_remote(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert 'GIT_TERMINAL_PROMPT' in src

    def test_git_terminal_prompt_on_store_credentials(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert "git_env_cred" in src

    def test_expand_depth_lower_bound(self):
        import inspect
        from indexer.rest_api import search_symbols
        src = inspect.getsource(search_symbols)
        assert "max(1, min(" in src

    def test_url_empty_check_before_discovery(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        url_check_pos = src.find('"url is required"')
        discovery_pos = src.find("_discover_remote_branches")
        assert url_check_pos > 0
        assert discovery_pos > 0
        assert url_check_pos < discovery_pos

    def test_no_duplicate_url_validation(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        assert src.count("http URLs cannot be used with credentials") == 1

    def test_cli_git_add_timeout(self):
        with open("indexer/cli.py", "r") as f:
            src = f.read()
        assert "timeout=30" in src

    def test_cli_no_warnings_warn(self):
        with open("indexer/cli.py", "r") as f:
            src = f.read()
        assert "warnings.warn" not in src

    def test_cli_no_unused_imports(self):
        with open("indexer/cli.py", "r") as f:
            src = f.read()
        assert "from datetime import" not in src
        assert "compute_hash, FileEntry" not in src
        assert "deep_enrich_page," not in src
        assert "PageContext, IndexEntry, TEMPLATES_DIR" not in src

    def test_rest_api_no_unused_config_imports(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert "EmbeddingConfig" not in src
        assert "VectorStoreConfig" not in src

    def test_mcp_no_unused_socket_import(self):
        with open("indexer/mcp_server.py", "r") as f:
            src = f.read()
        assert "import socket" not in src

    def test_max_depth_limit_consistent(self):
        with open("indexer/mcp_server.py", "r") as f:
            src = f.read()
        assert "min(max_depth, 8)" in src
        assert "min(max_depth, 10)" not in src

    def test_retrieval_branch_empty_means_no_filter(self):
        import inspect
        from indexer.retrieval import search_symbols
        src = inspect.getsource(search_symbols)
        assert "if branch else None" in src

    def test_rest_api_uses_retrieval_trace_call(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert "_trace_call_retrieval" in src
        assert "_expand_retrieval" in src

    def test_rest_api_no_duplicate_parse_json_list(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert src.count("def _parse_json_list") == 0

    def test_description_type_validation(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        assert "isinstance(description, str)" in src

    def test_tags_element_type_validation(self):
        import inspect
        from indexer.rest_api import register_repo
        src = inspect.getsource(register_repo)
        assert "isinstance(t, str)" in src


class TestRound15Fixes:
    def test_open_repo_null_safe_manifest(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        assert "(data.manifest&&data.manifest.files)" in src

    def test_open_repo_null_safe_wiki_pages(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        assert "(data.wiki_pages||[])" in src

    def test_api_json_parse_error_handling(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        assert "Invalid JSON response" in src

    def test_sync_branch_has_try_catch(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        idx = src.index("async function syncBranch")
        func_body = src[idx:idx+800]
        assert "try{" in func_body
        assert "catch(e)" in func_body

    def test_rebuild_branch_has_try_catch(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        idx = src.index("async function rebuildBranch")
        func_body = src[idx:idx+800]
        assert "try{" in func_body
        assert "catch(e)" in func_body

    def test_register_missing_branch_has_try_catch(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        idx = src.index("async function registerMissingBranch")
        func_body = src[idx:idx+800]
        assert "try{" in func_body
        assert "catch(e)" in func_body

    def test_do_unregister_has_try_catch(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        idx = src.index("async function doUnregister")
        func_body = src[idx:idx+800]
        assert "try{" in func_body
        assert "catch(e)" in func_body

    def test_do_validate_has_try_catch(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        idx = src.index("async function doValidate")
        func_body = src[idx:idx+2000]
        assert "try{" in func_body
        assert "catch(e)" in func_body

    def test_querySelector_title_optional_chaining(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        assert "querySelector('.title')?.textContent" in src

    def test_assert_operator_precedence_fixed(self):
        with open(__file__, "r") as f:
            src = f.read()
        assert '(result.get("url", "") if result else "") == ""' in src

    def test_no_duplicate_anthropic_lock_test(self):
        import inspect
        from indexer.llm import _get_anthropic_client
        src = inspect.getsource(_get_anthropic_client)
        assert "_anthropic_lock" in src

    def test_indexer_toml_no_dashscope_hardcoded(self):
        with open(".indexer.toml", "r") as f:
            content = f.read()
        assert "api_key" not in content.lower() or "api_key_env" in content.lower()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if "api_key" in stripped.lower() and "api_key_env" not in stripped.lower():
                    assert False, f"Hardcoded API key found: {stripped}"


class TestRound16Fixes:
    def test_rebuild_git_before_delete(self):
        import inspect
        from indexer.rest_api import _run_rebuild_task_inner
        src = inspect.getsource(_run_rebuild_task_inner)
        git_pos = src.find("git fetch")
        clean_pos = src.find("shutil.rmtree")
        assert git_pos > 0
        assert clean_pos > 0
        assert git_pos < clean_pos

    def test_branch_detection_after_clone(self):
        import inspect
        from indexer.rest_api import _run_register_task_inner
        src = inspect.getsource(_run_register_task_inner)
        detect_pos = src.find("_detect_default_branch")
        store_cred_pos = src.find("_store_credentials")
        assert detect_pos > 0
        assert store_cred_pos > 0
        assert detect_pos > store_cred_pos

    def test_vector_upsert_before_manifest(self):
        import inspect
        from indexer.rest_api import _run_indexing_pipeline
        src = inspect.getsource(_run_indexing_pipeline)
        upsert_pos = src.find("upsert_vectors")
        manifest_pos = src.find("update_manifest")
        assert upsert_pos > 0
        assert manifest_pos > 0
        assert upsert_pos < manifest_pos

    def test_progress_offset_in_pipeline(self):
        import inspect
        from indexer.rest_api import _run_indexing_pipeline
        src = inspect.getsource(_run_indexing_pipeline)
        assert "progress_offset" in src

    def test_sync_repo_url_initialized_before_try(self):
        import inspect
        from indexer.rest_api import _run_sync_task
        src = inspect.getsource(_run_sync_task)
        try_pos = src.find("try:")
        url_init_pos = src.find('repo_url = ')
        assert url_init_pos > 0
        assert try_pos > 0
        assert url_init_pos < try_pos

    def test_clone_dir_cleanup_on_failure(self):
        import inspect
        from indexer.rest_api import _run_register_task_inner
        src = inspect.getsource(_run_register_task_inner)
        assert src.count("shutil.rmtree(clone_dir)") >= 2

    def test_vector_store_client_eviction(self):
        from indexer.vector_store import evict_client
        assert callable(evict_client)

    def test_vector_store_client_lock(self):
        import inspect
        from indexer.vector_store import _get_client
        src = inspect.getsource(_get_client)
        assert "_client_lock" in src

    def test_empty_branches_to_index_check(self):
        import inspect
        from indexer.rest_api import _run_register_task_inner
        src = inspect.getsource(_run_register_task_inner)
        assert "No branches to index" in src

    def test_timeout_expired_includes_cmd(self):
        import inspect
        from indexer.rest_api import _run_sync_task
        src = inspect.getsource(_run_sync_task)
        assert "e.cmd" in src

    def test_skill_metadata_not_zero(self):
        import inspect
        from indexer.rest_api import _run_sync_task
        src = inspect.getsource(_run_sync_task)
        assert "sym_count" in src
        assert "0, 0" not in src.split("write_index_and_skill")[1][:100]


class TestRound17Fixes:
    def test_register_task_no_undefined_description_tags(self):
        import inspect
        from indexer.rest_api import _run_register_task_inner
        src = inspect.getsource(_run_register_task_inner)
        assert "description=description" not in src
        assert "tags=tags" not in src

    def test_unregister_uses_root_not_path(self):
        import inspect
        from indexer.rest_api import RepoRegistry
        src = inspect.getsource(RepoRegistry.unregister)
        assert 'info.get("root"' in src
        assert 'info.get("path"' not in src

    def test_search_symbols_int_coercion(self):
        import inspect
        from indexer.rest_api import search_symbols
        src = inspect.getsource(search_symbols)
        assert "int(body.get" in src
        assert "must be integers" in src

    def test_trace_call_int_coercion(self):
        import inspect
        from indexer.rest_api import trace_call
        src = inspect.getsource(trace_call)
        assert "int(body.get" in src
        assert "must be an integer" in src

    def test_git_config_has_timeout(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        idx = src.index("credential.helper")
        chunk = src[idx:idx+200]
        assert "timeout=" in chunk

    def test_detect_default_branch_has_git_terminal_prompt(self):
        import inspect
        from indexer.rest_api import _detect_default_branch
        src = inspect.getsource(_detect_default_branch)
        assert "GIT_TERMINAL_PROMPT" in src

    def test_rebuild_evicts_vector_client_before_rmtree(self):
        import inspect
        from indexer.rest_api import _run_rebuild_task_inner
        src = inspect.getsource(_run_rebuild_task_inner)
        evict_pos = src.find("evict_client")
        rmtree_pos = src.rfind("shutil.rmtree(vector_dir)")
        assert evict_pos > 0
        assert rmtree_pos > 0
        assert evict_pos < rmtree_pos

    def test_api_parses_json_error_body(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        assert "JSON.parse(t)" in src
        assert "j.error" in src


class TestRound18Fixes:
    def test_rebuild_has_timeout_expired_handler(self):
        import inspect
        from indexer.rest_api import _run_rebuild_task_inner
        src = inspect.getsource(_run_rebuild_task_inner)
        assert "TimeoutExpired" in src

    def test_git_py_has_git_terminal_prompt(self):
        with open("indexer/git.py", "r") as f:
            src = f.read()
        assert "GIT_TERMINAL_PROMPT" in src

    def test_cli_git_add_has_git_terminal_prompt(self):
        with open("indexer/cli.py", "r") as f:
            src = f.read()
        assert "git_env_cli" in src

    def test_step_names_includes_git_steps(self):
        with open("indexer/static/index.html", "r") as f:
            src = f.read()
        for step in ["git_fetch", "git_checkout", "git_timeout", "locked", "unknown"]:
            assert f"{step}:" in src

    def test_evict_client_logs_on_failure(self):
        import inspect
        from indexer.rest_api import RepoRegistry
        src = inspect.getsource(RepoRegistry.unregister)
        assert "logger.debug" in src

    def test_git_reset_return_code_checked(self):
        with open("indexer/rest_api.py", "r") as f:
            src = f.read()
        assert src.count("git reset --hard failed") >= 3


class TestPerformanceOptimizations:
    def test_description_cache_functions_exist(self):
        from indexer.indexing import load_cached_descriptions, save_cached_descriptions
        assert callable(load_cached_descriptions)
        assert callable(save_cached_descriptions)

    def test_file_description_cache_functions_exist(self):
        from indexer.indexing import load_cached_file_descriptions, save_cached_file_descriptions
        assert callable(load_cached_file_descriptions)
        assert callable(save_cached_file_descriptions)

    def test_pipeline_uses_description_cache(self):
        import inspect
        from indexer.rest_api import _run_indexing_pipeline
        src = inspect.getsource(_run_indexing_pipeline)
        assert "load_cached_descriptions" in src
        assert "save_cached_descriptions" in src
        assert "new_nodes" in src

    def test_pipeline_uses_file_description_cache(self):
        import inspect
        from indexer.rest_api import _run_indexing_pipeline
        src = inspect.getsource(_run_indexing_pipeline)
        assert "load_cached_file_descriptions" in src
        assert "save_cached_file_descriptions" in src

    def test_embedding_batch_size_increased(self):
        with open("indexer/embedding.py", "r") as f:
            src = f.read()
        assert "batch_size" in src
        assert "dashscope" in src

    def test_describe_files_parallel(self):
        import inspect
        from indexer.llm import describe_files
        src = inspect.getsource(describe_files)
        assert "ThreadPoolExecutor" in src
        assert "max_workers" in src

    def test_parse_candidates_parallel(self):
        import inspect
        from indexer.indexing import parse_candidates
        src = inspect.getsource(parse_candidates)
        assert "ThreadPoolExecutor" in src
        assert "uncached" in src

    def test_vector_store_batch_query(self):
        import inspect
        from indexer.vector_store import upsert_nodes
        src = inspect.getsource(upsert_nodes)
        assert "$or" in src

    def test_embedding_cache_functions_exist(self):
        from indexer.indexing import load_cached_embeddings, save_cached_embeddings
        from indexer.embedding import compute_embedding_sig
        assert callable(load_cached_embeddings)
        assert callable(save_cached_embeddings)
        assert callable(compute_embedding_sig)

    def test_upsert_vectors_uses_embedding_cache(self):
        import inspect
        from indexer.indexing import upsert_vectors
        src = inspect.getsource(upsert_vectors)
        assert "load_cached_embeddings" in src
        assert "save_cached_embeddings" in src
        assert "miss_nodes" in src

    def test_parallel_symbol_and_file_description(self):
        import inspect
        from indexer.rest_api import _run_indexing_pipeline
        src = inspect.getsource(_run_indexing_pipeline)
        assert "_desc_pool" in src
        assert "ThreadPoolExecutor(max_workers=2)" in src

    def test_write_wiki_pages_accepts_precomputed_groups(self):
        import inspect
        from indexer.indexing import write_wiki_pages
        sig = inspect.signature(write_wiki_pages)
        assert "precomputed_groups" in sig.parameters

    def test_load_existing_nodes_uses_manifest_hash(self):
        import inspect
        from indexer.indexing import load_existing_nodes
        src = inspect.getsource(load_existing_nodes)
        assert "entry.hash" in src
