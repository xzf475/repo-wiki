from __future__ import annotations
import hashlib
import os
import json
import logging
import threading
from pathlib import Path
from indexer.ast_parser import ASTNode
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


def build_embedding_text(node: ASTNode, description: str = "") -> str:
    parts = [
        f"[{node.type}] {node.id}",
        f"Lines {node.line_start}-{node.line_end}",
    ]
    if description:
        parts.append(description)
    if node.docstring:
        parts.append(f"Docstring: {node.docstring}")
    if node.calls:
        parts.append(f"Calls: {', '.join(node.calls[:10])}")
    if node.called_by:
        parts.append(f"Called by: {', '.join(node.called_by[:10])}")
    if node.imports:
        parts.append(f"Imports: {', '.join(node.imports[:6])}")
    return "\n".join(parts)


def compute_embedding_sig(node: ASTNode, description: str = "") -> str:
    text = build_embedding_text(node, description)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def embed_nodes(
    nodes: list[ASTNode],
    descriptions: dict[str, str],
    cfg: EmbeddingConfig,
    max_workers: int = 8,
) -> dict[str, list[float]]:
    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise ValueError(
            f"Embedding API key not found. Set {cfg.api_key_env} env var or configure api_key_env in .indexer.toml"
        )

    texts = [build_embedding_text(n, descriptions.get(n.id, "")) for n in nodes]
    ids = [n.id for n in nodes]

    result: dict[str, list[float]] = {}
    batch_size = 10 if "dashscope" in cfg.provider.lower() else 50
    batches = []
    for i in range(0, len(texts), batch_size):
        batches.append((
            texts[i:i + batch_size],
            ids[i:i + batch_size],
        ))

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_call_embedding_api, batch_texts, cfg, api_key): batch_ids for batch_texts, batch_ids in batches}
        for future in as_completed(futures):
            batch_ids = futures[future]
            try:
                vectors = future.result()
                for bid, vec in zip(batch_ids, vectors):
                    result[bid] = vec
            except Exception as e:
                logger.warning("Embedding batch failed (%d ids): %s", len(batch_ids), e)

    if len(result) < len(ids):
        logger.error("Embedding incomplete: %d/%d nodes succeeded", len(result), len(ids))
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

