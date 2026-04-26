from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from indexer.ast_parser import ASTNode
from indexer.config import EmbeddingConfig
from indexer.utils import load_env_file

logger = logging.getLogger(__name__)

_MODELS_WITHOUT_DIMENSIONS = {"text-embedding-ada-002"}


def _resolve_api_key(cfg: EmbeddingConfig) -> str | None:
    load_env_file()
    value = cfg.api_key_env
    if not value:
        return os.environ.get("DASHSCOPE_API_KEY")
    if " " not in value and not value.isupper() and not value.replace("_", "").isupper():
        return value
    return os.environ.get(value)


def _build_text(node: ASTNode, description: str = "") -> str:
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


def embed_nodes(
    nodes: list[ASTNode],
    descriptions: dict[str, str],
    cfg: EmbeddingConfig,
    max_workers: int = 4,
) -> dict[str, list[float]]:
    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise ValueError(
            f"Embedding API key not found. Set {cfg.api_key_env} env var or configure api_key_env in .indexer.toml"
        )

    texts = [_build_text(n, descriptions.get(n.id, "")) for n in nodes]
    ids = [n.id for n in nodes]

    result: dict[str, list[float]] = {}
    batch_size = 10
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
                for bid in batch_ids:
                    result[bid] = None

    return result


def embed_query(query: str, cfg: EmbeddingConfig) -> list[float]:
    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise ValueError(f"Embedding API key not found. Set {cfg.api_key_env} env var")

    vectors = _call_embedding_api([query], cfg, api_key)
    return vectors[0]


def _call_embedding_api(
    texts: list[str],
    cfg: EmbeddingConfig,
    api_key: str,
) -> list[list[float]]:
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=cfg.base_url,
    )

    model_name = cfg.provider.removeprefix("dashscope/")

    kwargs = dict(model=model_name, input=texts, encoding_format="float")
    if cfg.dimensions and model_name not in _MODELS_WITHOUT_DIMENSIONS:
        kwargs["dimensions"] = cfg.dimensions
    response = client.embeddings.create(**kwargs)

    vectors = []
    for item in sorted(response.data, key=lambda x: x.index):
        vectors.append(item.embedding)
    return vectors
