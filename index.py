"""Index local documents into a persisted ChromaDB vector database."""

from __future__ import annotations

import os
import textwrap

from src.chunking import TextChunker
from src.embeddings import create_embedder
from src.loaders import DocumentLoader
from src.utils.config import get_env, load_project_env
from src.vectorstore import ChromaStore


def print_sample_chunks(chunks: list, sample_size: int = 2) -> None:
    for number, chunk in enumerate(chunks[:sample_size], start=1):
        preview = textwrap.shorten(chunk.text.replace("\n", " "), width=300)
        print(f"\nSample chunk {number}")
        print(f"  chunk_id: {chunk.chunk_id}")
        print(f"  source: {chunk.source}")
        print(f"  file_path: {chunk.file_path}")
        print(f"  file_type: {chunk.file_type}")
        print(f"  page_number: {chunk.page_number}")
        print(f"  chunk_index: {chunk.chunk_index}")
        print(f"  preview: {preview}")


def main() -> None:
    load_project_env()

    data_dir = get_env("DATA_DIR", "data")

    try:
        loader = DocumentLoader(data_dir=data_dir)
        files = loader.list_files()
        pages = loader.load_documents()

        chunker = TextChunker()
        chunks = chunker.chunk_documents(pages)

        if not chunks:
            raise RuntimeError("No chunks were created from the loaded documents.")

        embedding_batch_size = int(get_env("EMBEDDING_BATCH_SIZE", "32"))
        embedder = create_embedder()
        embeddings = embedder.embed_documents(
            [chunk.text for chunk in chunks],
            batch_size=embedding_batch_size,
        )

        vector_store = ChromaStore()
        vector_store.reset_collection()
        vector_store.add_chunks(chunks, embeddings)
        vectors_stored = vector_store.count()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print("Indexing summary")
    print(f"Files found: {len(files)}")
    print(f"Document pages/sections extracted: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunk size: {chunker.chunk_size}")
    print(f"Chunk overlap: {chunker.chunk_overlap}")
    print(f"Embedding model: {embedder.model_name}")
    print(f"Embedding batch size: {embedding_batch_size}")
    print(f"Vector database path: {vector_store.persist_dir}")
    print(f"Collection name: {vector_store.collection_name}")
    print(f"Vectors stored: {vectors_stored}")

    if chunks:
        print_sample_chunks(chunks)


if __name__ == "__main__":
    main()
