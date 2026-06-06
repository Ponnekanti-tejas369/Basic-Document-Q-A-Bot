"""ChromaDB vector store for persisted document chunks."""

from __future__ import annotations

import os
from pathlib import Path

from src.utils.schemas import DocumentChunk

DEFAULT_CHROMA_PERSIST_DIR = "vector_db"
DEFAULT_CHROMA_COLLECTION_NAME = "document_chunks"


class ChromaStore:
    """Persist chunk embeddings and metadata in ChromaDB."""

    def __init__(
        self,
        persist_dir: str | Path | None = None,
        collection_name: str | None = None,
        create_if_missing: bool = True,
    ) -> None:
        self.persist_dir = Path(
            persist_dir or os.getenv("CHROMA_PERSIST_DIR", DEFAULT_CHROMA_PERSIST_DIR)
        )
        self.collection_name = (
            collection_name
            or os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_CHROMA_COLLECTION_NAME)
        )
        self.create_if_missing = create_if_missing
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = self._create_client()
        self._collection = self._get_collection()

    def reset_collection(self) -> None:
        """Delete and recreate the configured collection."""

        try:
            self._client.delete_collection(name=self.collection_name)
        except Exception:
            pass

        self._collection = self._client.get_or_create_collection(
            name=self.collection_name
        )

    def add_chunks(
        self, chunks: list[DocumentChunk], embeddings: list[list[float]]
    ) -> None:
        """Store chunks and their embeddings in ChromaDB."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embedding vectors. "
                f"Got {len(chunks)} chunks and {len(embeddings)} embeddings."
            )

        if not chunks:
            return

        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name
            )

        self._collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[self._metadata_from_chunk(chunk) for chunk in chunks],
        )

    def count(self) -> int:
        """Return the number of vectors stored in the collection."""

        if self._collection is None:
            return 0

        return int(self._collection.count())

    def similarity_search(
        self, query_embedding: list[float], top_k: int
    ) -> list[dict[str, object]]:
        """Return the top-k chunks most similar to a query embedding."""

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if self._collection is None or self.count() == 0:
            raise ValueError(
                "No indexed documents found. Please add documents to data/ "
                "and run python index.py first."
            )

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.count()),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            raise RuntimeError(f"ChromaDB similarity search failed: {exc}") from exc

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: list[dict[str, object]] = []
        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index] or {}
            matches.append(
                {
                    "chunk_id": chunk_id,
                    "text": documents[index],
                    "source": metadata.get("source", ""),
                    "file_path": metadata.get("file_path", ""),
                    "file_type": metadata.get("file_type", ""),
                    "page_number": metadata.get("page_number", ""),
                    "chunk_index": metadata.get("chunk_index", ""),
                    "score": distances[index] if index < len(distances) else None,
                    "metadata": metadata,
                }
            )

        return matches

    def _metadata_from_chunk(self, chunk: DocumentChunk) -> dict[str, object]:
        return {
            "source": chunk.source,
            "file_path": chunk.file_path,
            "file_type": chunk.file_type,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
        }

    def _create_client(self):
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "chromadb is required for vector storage. Install it with "
                "`pip install chromadb`."
            ) from exc

        try:
            return chromadb.PersistentClient(path=str(self.persist_dir))
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize ChromaDB at {self.persist_dir}: {exc}"
            ) from exc

    def _get_collection(self):
        if self.create_if_missing:
            return self._client.get_or_create_collection(name=self.collection_name)

        try:
            return self._client.get_collection(name=self.collection_name)
        except Exception:
            return None
