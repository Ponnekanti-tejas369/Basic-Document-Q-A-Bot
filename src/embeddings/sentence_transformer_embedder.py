"""sentence-transformers embedding implementation."""

from __future__ import annotations

import os

from src.embeddings.base_embedder import BaseEmbedder

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SentenceTransformerEmbedder(BaseEmbedder):
    """Local embedding provider backed by sentence-transformers."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        )
        self._model = self._load_model()

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_documents(
        self, texts: list[str], batch_size: int = 32
    ) -> list[list[float]]:
        if not texts:
            return []

        clean_texts = [text.strip() for text in texts]
        try:
            embeddings = self._model.encode(
                clean_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to embed document chunks: {exc}") from exc

        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        try:
            embedding = self._model.encode(
                text.strip(),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to embed query text: {exc}") from exc

        return embedding.tolist()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install it with `pip install sentence-transformers`."
            ) from exc

        try:
            return SentenceTransformer(self._model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{self._model_name}'. "
                "Check the model name and your local package/network setup."
            ) from exc

