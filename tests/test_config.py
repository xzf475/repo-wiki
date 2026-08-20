# tests/test_config.py
import os
import tempfile
from pathlib import Path
from indexer.config import Config, load_config, save_config

_ENV_VARS = [
    "EMBEDDING_PROVIDER", "EMBEDDING_API_KEY_ENV", "EMBEDDING_BASE_URL", "EMBEDDING_DIMENSIONS",
    "DASHSCOPE_API_KEY",
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
                wiki_dir="docs/wiki",
                merge_threshold=4,
                pre_commit=True,
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
            toml_content = b"[indexer]\nwiki_dir = \"docs/wiki\"\n"
            (Path(d) / ".indexer.toml").write_bytes(toml_content)
            cfg = load_config(Path(d))
            assert cfg.wiki_dir == "docs/wiki"
            assert cfg.embedding == Config().embedding
            assert cfg.pre_commit == Config().pre_commit
    finally:
        _restore_env(saved)
