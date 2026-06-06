"""Base interface for embedding providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """Interface implemented by all embedding providers."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the embedding model in use."""

    @abstractmethod
    def embed_documents(
        self, texts: list[str], batch_size: int = 32
    ) -> list[list[float]]:
        """Embed multiple document chunks in batches."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query for later retrieval."""

