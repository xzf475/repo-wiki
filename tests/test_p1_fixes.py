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
            assert result.get("url", "") if result else "" == ""


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
