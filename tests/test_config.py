# tests/test_config.py
import os
import tempfile
from pathlib import Path
from indexer.config import Config, load_config, save_config

_ENV_VARS = [
    "LLM_PROVIDER", "LLM_BASE_URL", "LLM_API_KEY_ENV",
    "EMBEDDING_PROVIDER", "EMBEDDING_API_KEY_ENV", "EMBEDDING_BASE_URL", "EMBEDDING_DIMENSIONS",
    "VECTOR_BACKEND", "VECTOR_PERSIST_DIR", "VECTOR_COLLECTION_NAME",
    "DASHSCOPE_API_KEY", "ANTHROPIC_API_KEY",
]


def _clean_env():
    import indexer.utils as utils_mod
    utils_mod._env_loaded = True
    saved = {}
    for k in _ENV_VARS:
        if k in os.environ:
            saved[k] = os.environ.pop(k)
    return saved


def _restore_env(saved):
    for k, v in saved.items():
        os.environ[k] = v


def test_load_defaults():
    saved = _clean_env()
    try:
        with tempfile.TemporaryDirectory() as d:
            cfg = load_config(Path(d))
            assert cfg == Config()
    finally:
        _restore_env(saved)


def test_save_and_reload():
    saved = _clean_env()
    try:
        with tempfile.TemporaryDirectory() as d:
            cfg = Config(
                provider="openai/gpt-4o",
                api_key_env="OPENAI_API_KEY",
                base_url="https://api.openai.com/v1",
                wiki_dir="docs/wiki",
                ignore=["node_modules"],
                max_tokens_per_batch=4000,
                pre_commit=True,
                synthesize_commit_message=False,
            )
            save_config(Path(d), cfg)
            reloaded = load_config(Path(d))
            assert reloaded == cfg
    finally:
        _restore_env(saved)


def test_partial_toml_uses_defaults():
    saved = _clean_env()
    try:
        with tempfile.TemporaryDirectory() as d:
            toml_content = b"[llm]\nprovider = \"openai/gpt-4o\"\n"
            (Path(d) / ".indexer.toml").write_bytes(toml_content)
            cfg = load_config(Path(d))
            assert cfg.provider == "openai/gpt-4o"
            assert cfg.wiki_dir == Config().wiki_dir
            assert cfg.pre_commit == Config().pre_commit
    finally:
        _restore_env(saved)