from __future__ import annotations

from collections.abc import Sequence

from indexer.config import EmbeddingConfig
from indexer.embedding import embed_query, embed_texts


class ConfiguredEmbeddingProvider:
    """RepositoryIndex adapter for the configured OpenAI-compatible endpoint."""

    def __init__(self, config: EmbeddingConfig):
        self._config = config
        self.model = f"{config.provider}@{config.dimensions}"

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return embed_texts(list(texts), self._config)

    def embed_query(self, text: str) -> list[float]:
        return embed_query(text, self._config)


__all__ = ["ConfiguredEmbeddingProvider"]
