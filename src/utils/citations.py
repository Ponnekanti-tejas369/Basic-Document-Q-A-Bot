"""Citation formatting helpers."""

from __future__ import annotations


def format_citation(metadata: dict[str, object]) -> str:
    """Format chunk metadata as a source citation."""

    source = metadata.get("source", "unknown")
    page_number = metadata.get("page_number", "unknown")
    chunk_index = metadata.get("chunk_index", "unknown")

    return f"[source: {source}, page/section: {page_number}, chunk: {chunk_index}]"
