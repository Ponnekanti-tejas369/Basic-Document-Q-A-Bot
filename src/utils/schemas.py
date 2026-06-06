"""Shared data structures for document loading and chunking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentPage:
    """Extracted text unit from a source document."""

    text: str
    source: str
    file_path: str
    file_type: str
    page_number: int


@dataclass(frozen=True)
class DocumentChunk:
    """Chunk of text ready for later embedding and retrieval."""

    text: str
    source: str
    file_path: str
    file_type: str
    page_number: int
    chunk_index: int
    chunk_id: str

