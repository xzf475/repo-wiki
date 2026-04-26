from __future__ import annotations
import os
import tomllib
import tomli_w
from dataclasses import dataclass, field
from pathlib import Path

from indexer.utils import load_env_file

FILENAME = ".indexer.toml"

_ENV_MAP = {
    "llm_provider": "LLM_PROVIDER",
    "llm_base_url": "LLM_BASE_URL",
    "llm_api_key_env": "LLM_API_KEY_ENV",
    "embedding_provider": "EMBEDDING_PROVIDER",
    "embedding_api_key_env": "EMBEDDING_API_KEY_ENV",
    "embedding_base_url": "EMBEDDING_BASE_URL",
    "embedding_dimensions": "EMBEDDING_DIMENSIONS",
    "vector_backend": "VECTOR_BACKEND",
    "vector_persist_dir": "VECTOR_PERSIST_DIR",
    "vector_collection_name": "VECTOR_COLLECTION_NAME",
}

@dataclass
class EmbeddingConfig:
    provider: str = "dashscope/text-embedding-v4"
    api_key_env: str = "DASHSCOPE_API_KEY"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dimensions: int = 1024

@dataclass
class VectorStoreConfig:
    backend: str = "chromadb"
    persist_dir: str = ".indexer/vector_db"
    collection_name: str = "repo_wiki_code"

@dataclass
class Config:
    provider: str = "anthropic/claude-sonnet-4-6"
    api_key_env: str = "ANTHROPIC_API_KEY"
    base_url: str = ""
    wiki_dir: str = "wiki"
    ignore: list[str] = field(default_factory=lambda: [
        "node_modules", ".venv", "dist", "build", "__pycache__", "*.test.*"
    ])
    max_tokens_per_batch: int = 8000
    merge_threshold: int = 2
    pre_commit: bool = True
    synthesize_commit_message: bool = True
    deep_hook: bool = True
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)


def _env(key: str, default: str | None = None) -> str | None:
    env_name = _ENV_MAP.get(key)
    if env_name and env_name in os.environ:
        return os.environ[env_name]
    return default


def _env_int(key: str, default: int) -> int:
    env_name = _ENV_MAP.get(key)
    if env_name and env_name in os.environ:
        try:
            return int(os.environ[env_name])
        except ValueError:
            return default
    return default


def load_config(repo_root: Path) -> Config:
    load_env_file()
    path = repo_root / FILENAME
    if not path.exists():
        return _apply_env(Config())
    defaults = Config()
    emb_defaults = EmbeddingConfig()
    vs_defaults = VectorStoreConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    llm = data.get("llm", {})
    idx = data.get("indexer", {})
    hooks = data.get("hooks", {})
    emb = data.get("embedding", {})
    vs = data.get("vector_store", {})
    cfg = Config(
        provider=llm.get("provider", defaults.provider),
        api_key_env=llm.get("api_key_env", defaults.api_key_env),
        base_url=llm.get("base_url", defaults.base_url),
        wiki_dir=idx.get("wiki_dir", defaults.wiki_dir),
        ignore=list(idx.get("ignore", defaults.ignore)),
        max_tokens_per_batch=idx.get("max_tokens_per_batch", defaults.max_tokens_per_batch),
        merge_threshold=idx.get("merge_threshold", defaults.merge_threshold),
        pre_commit=hooks.get("pre_commit", defaults.pre_commit),
        synthesize_commit_message=hooks.get("synthesize_commit_message", defaults.synthesize_commit_message),
        deep_hook=hooks.get("deep", defaults.deep_hook),
        embedding=EmbeddingConfig(
            provider=emb.get("provider", emb_defaults.provider),
            api_key_env=emb.get("api_key_env", emb_defaults.api_key_env),
            base_url=emb.get("base_url", emb_defaults.base_url),
            dimensions=emb.get("dimensions", emb_defaults.dimensions),
        ),
        vector_store=VectorStoreConfig(
            backend=vs.get("backend", vs_defaults.backend),
            persist_dir=vs.get("persist_dir", vs_defaults.persist_dir),
            collection_name=vs.get("collection_name", vs_defaults.collection_name),
        ),
    )
    return _apply_env(cfg)


def _apply_env(cfg: Config) -> Config:
    cfg.provider = _env("llm_provider", cfg.provider) or cfg.provider
    cfg.api_key_env = _env("llm_api_key_env", cfg.api_key_env) or cfg.api_key_env
    cfg.base_url = _env("llm_base_url", cfg.base_url) or cfg.base_url
    cfg.embedding.provider = _env("embedding_provider", cfg.embedding.provider) or cfg.embedding.provider
    cfg.embedding.api_key_env = _env("embedding_api_key_env", cfg.embedding.api_key_env) or cfg.embedding.api_key_env
    cfg.embedding.base_url = _env("embedding_base_url", cfg.embedding.base_url) or cfg.embedding.base_url
    cfg.embedding.dimensions = _env_int("embedding_dimensions", cfg.embedding.dimensions)
    cfg.vector_store.backend = _env("vector_backend", cfg.vector_store.backend) or cfg.vector_store.backend
    cfg.vector_store.persist_dir = _env("vector_persist_dir", cfg.vector_store.persist_dir) or cfg.vector_store.persist_dir
    cfg.vector_store.collection_name = _env("vector_collection_name", cfg.vector_store.collection_name) or cfg.vector_store.collection_name
    return cfg


def save_config(repo_root: Path, cfg: Config) -> None:
    data = {
        "llm": {"provider": cfg.provider, "api_key_env": cfg.api_key_env, "base_url": cfg.base_url},
        "indexer": {"wiki_dir": cfg.wiki_dir, "ignore": cfg.ignore, "max_tokens_per_batch": cfg.max_tokens_per_batch, "merge_threshold": cfg.merge_threshold},
        "hooks": {"pre_commit": cfg.pre_commit, "synthesize_commit_message": cfg.synthesize_commit_message, "deep": cfg.deep_hook},
        "embedding": {"provider": cfg.embedding.provider, "api_key_env": cfg.embedding.api_key_env, "base_url": cfg.embedding.base_url, "dimensions": cfg.embedding.dimensions},
        "vector_store": {"backend": cfg.vector_store.backend, "persist_dir": cfg.vector_store.persist_dir, "collection_name": cfg.vector_store.collection_name},
    }
    with open(repo_root / FILENAME, "wb") as f:
        tomli_w.dump(data, f)
