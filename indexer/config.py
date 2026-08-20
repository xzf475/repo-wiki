from __future__ import annotations
import logging
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

from indexer.utils import load_env_file

FILENAME = ".indexer.toml"

_ENV_MAP = {
    "embedding_provider": "EMBEDDING_PROVIDER",
    "embedding_api_key_env": "EMBEDDING_API_KEY_ENV",
    "embedding_base_url": "EMBEDDING_BASE_URL",
    "embedding_dimensions": "EMBEDDING_DIMENSIONS",
}

@dataclass
class EmbeddingConfig:
    provider: str = "dashscope/text-embedding-v4"
    api_key_env: str = "DASHSCOPE_API_KEY"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dimensions: int = 1024

@dataclass
class Config:
    wiki_dir: str = "wiki"
    merge_threshold: int = 2
    pre_commit: bool = True
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)


def _env(key: str, default: str | None = None) -> str | None:
    env_name = _ENV_MAP.get(key)
    if env_name and env_name in os.environ:
        return os.environ[env_name]
    return default


def _apply_env_field(env_val: str | None, current: str) -> str:
    if env_val is not None and env_val != "":
        return env_val
    return current


def _env_int(key: str, default: int) -> int:
    env_name = _ENV_MAP.get(key)
    if env_name and env_name in os.environ:
        try:
            return int(os.environ[env_name])
        except ValueError:
            logger.warning("Invalid int value for %s=%r, using default %d", env_name, os.environ[env_name], default)
            return default
    return default


def load_config(repo_root: Path) -> Config:
    load_env_file()
    path = repo_root / FILENAME
    if not path.exists():
        return _apply_env(Config())
    defaults = Config()
    emb_defaults = EmbeddingConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    idx = data.get("indexer", {})
    hooks = data.get("hooks", {})
    emb = data.get("embedding", {})
    cfg = Config(
        wiki_dir=idx.get("wiki_dir", defaults.wiki_dir),
        merge_threshold=idx.get("merge_threshold", defaults.merge_threshold),
        pre_commit=hooks.get("pre_commit", defaults.pre_commit),
        embedding=EmbeddingConfig(
            provider=emb.get("provider", emb_defaults.provider),
            api_key_env=emb.get("api_key_env", emb_defaults.api_key_env),
            base_url=emb.get("base_url", emb_defaults.base_url),
            dimensions=emb.get("dimensions", emb_defaults.dimensions),
        ),
    )
    cfg = _apply_env(cfg)
    if cfg.merge_threshold < 1:
        logger.warning("merge_threshold must be >= 1, got %d; resetting to 2", cfg.merge_threshold)
        cfg.merge_threshold = 2
    if cfg.embedding.dimensions < 1:
        logger.warning("embedding.dimensions must be >= 1, got %d; resetting to 1024", cfg.embedding.dimensions)
        cfg.embedding.dimensions = 1024
    return cfg


def _apply_env(cfg: Config) -> Config:
    cfg.embedding.provider = _apply_env_field(_env("embedding_provider", None), cfg.embedding.provider)
    cfg.embedding.api_key_env = _apply_env_field(_env("embedding_api_key_env", None), cfg.embedding.api_key_env)
    cfg.embedding.base_url = _apply_env_field(_env("embedding_base_url", None), cfg.embedding.base_url)
    cfg.embedding.dimensions = _env_int("embedding_dimensions", cfg.embedding.dimensions)
    return cfg


def save_config(repo_root: Path, cfg: Config) -> None:
    data = {
        "indexer": {"wiki_dir": cfg.wiki_dir, "merge_threshold": cfg.merge_threshold},
        "hooks": {"pre_commit": cfg.pre_commit},
        "embedding": {"provider": cfg.embedding.provider, "api_key_env": cfg.embedding.api_key_env, "base_url": cfg.embedding.base_url, "dimensions": cfg.embedding.dimensions},
    }
    import tempfile
    import tomli_w
    target = repo_root / FILENAME
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(dir=str(repo_root), suffix=".toml.tmp", delete=False) as f:
            tomli_w.dump(data, f)
            tmp_path = f.name
        os.replace(tmp_path, str(target))
    except OSError:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise
