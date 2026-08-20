from __future__ import annotations
import logging
import threading
from indexer.config import EmbeddingConfig
from indexer.utils import load_env_file, resolve_api_key

logger = logging.getLogger(__name__)

_MODELS_WITHOUT_DIMENSIONS = {"text-embedding-ada-002"}
_openai_client = None
_openai_client_base_url: str | None = None
_openai_lock = threading.Lock()

def _get_openai_client(api_key: str, base_url: str) -> "OpenAI":
    global _openai_client, _openai_client_base_url
    with _openai_lock:
        from openai import OpenAI
        if _openai_client is None or _openai_client.api_key != api_key or _openai_client_base_url != base_url:
            _openai_client = OpenAI(api_key=api_key, base_url=base_url)
            _openai_client_base_url = base_url
        return _openai_client


_EMBEDDING_KEY_ENVS = ["DASHSCOPE_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]


def _resolve_api_key(cfg: EmbeddingConfig) -> str | None:
    load_env_file()
    return resolve_api_key(cfg.api_key_env, _EMBEDDING_KEY_ENVS)


def embed_texts(texts: list[str], cfg: EmbeddingConfig) -> list[list[float]]:
    """Embed an ordered batch atomically; any failed sub-batch raises."""
    if not texts:
        return []
    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise ValueError(
            f"Embedding API key not found. Set {cfg.api_key_env} env var or configure api_key_env in .indexer.toml"
        )
    batch_size = 10 if "dashscope" in cfg.provider.lower() else 50
    batches = [texts[start:start + batch_size] for start in range(0, len(texts), batch_size)]
    if len(batches) == 1:
        return _call_embedding_api(batches[0], cfg, api_key)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    ordered: list[list[list[float]] | None] = [None] * len(batches)
    with ThreadPoolExecutor(max_workers=min(8, len(batches))) as pool:
        futures = {
            pool.submit(_call_embedding_api, batch, cfg, api_key): index
            for index, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            ordered[futures[future]] = future.result()
    result = [vector for batch in ordered if batch is not None for vector in batch]
    if len(result) != len(texts):
        raise ValueError(
            f"Embedding API returned {len(result)} vectors for {len(texts)} inputs"
        )
    return result


def embed_query(query: str, cfg: EmbeddingConfig) -> list[float]:
    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise ValueError(f"Embedding API key not found. Set {cfg.api_key_env} env var")

    vectors = _call_embedding_api([query], cfg, api_key)
    if not vectors:
        raise ValueError(f"Embedding API returned empty result for query: {query[:50]}")
    return vectors[0]


def _call_embedding_api(
    texts: list[str],
    cfg: EmbeddingConfig,
    api_key: str,
) -> list[list[float]]:
    import random as _random
    import time as _time
    from openai import RateLimitError, APIConnectionError, APITimeoutError

    client = _get_openai_client(api_key, cfg.base_url)

    model_name = cfg.provider.split("/", 1)[-1] if "/" in cfg.provider else cfg.provider

    kwargs = dict(model=model_name, input=texts)
    if model_name not in _MODELS_WITHOUT_DIMENSIONS:
        kwargs["encoding_format"] = "float"
    if cfg.dimensions and model_name not in _MODELS_WITHOUT_DIMENSIONS:
        kwargs["dimensions"] = cfg.dimensions

    for attempt in range(3):
        try:
            response = client.embeddings.create(**kwargs)
            vectors = []
            for item in sorted(response.data, key=lambda x: x.index):
                vectors.append(item.embedding)
            return vectors
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            if attempt >= 2:
                raise
            delay = 2.0 * (2 ** attempt) + _random.uniform(0, 1)
            logger.warning("Embedding API retryable error (attempt %d): %s, retrying in %.1fs", attempt + 1, e, delay)
            _time.sleep(delay)
