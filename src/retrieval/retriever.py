"""Retriever service for query embedding and vector search."""

from __future__ import annotations

from src.embeddings.base_embedder import BaseEmbedder
from src.vectorstore.chroma_store import ChromaStore


class Retriever:
    """Retrieve relevant chunks for a natural language query."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        vector_store: ChromaStore,
        top_k: int = 5,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> list[dict[str, object]]:
        """Embed a query and return matching source chunks."""

        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Query cannot be empty.")

        query_embedding = self.embedder.embed_query(clean_query)
        return self.vector_store.similarity_search(query_embedding, self.top_k)

