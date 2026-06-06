"""Factory for embedding providers."""

from __future__ import annotations

import os

from src.embeddings.base_embedder import BaseEmbedder
from src.embeddings.sentence_transformer_embedder import SentenceTransformerEmbedder

DEFAULT_EMBEDDING_PROVIDER = "sentence-transformers"


def create_embedder() -> BaseEmbedder:
    """Create the configured embedding provider."""

    provider = os.getenv("EMBEDDING_PROVIDER", DEFAULT_EMBEDDING_PROVIDER)
    provider = provider.strip().lower()

    if provider in {"sentence-transformers", "sentence_transformers", "local"}:
        return SentenceTransformerEmbedder()

    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER '{provider}'. "
        "Supported provider: sentence-transformers."
    )

