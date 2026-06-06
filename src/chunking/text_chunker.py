"""Fixed-size overlapping text chunker."""

from __future__ import annotations

import os
import re

from src.utils.schemas import DocumentChunk, DocumentPage

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


class TextChunker:
    """Split document pages into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.chunk_size = chunk_size or self._read_positive_int(
            "CHUNK_SIZE", DEFAULT_CHUNK_SIZE
        )
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else self._read_non_negative_int(
            "CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP
        )
        self._validate_config()

    def chunk_documents(self, pages: list[DocumentPage]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        for page in pages:
            page_chunks = self.chunk_page(page)
            chunks.extend(page_chunks)

        return chunks

    def chunk_page(self, page: DocumentPage) -> list[DocumentChunk]:
        text = page.text.strip()
        if not text:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_index = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = self._build_chunk_id(page, chunk_index)
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        source=page.source,
                        file_path=page.file_path,
                        file_type=page.file_type,
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        chunk_id=chunk_id,
                    )
                )
                chunk_index += 1

            if end >= text_length:
                break

            start = end - self.chunk_overlap

        return chunks

    def _validate_config(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be greater than 0.")

        if self.chunk_overlap < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative.")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")

    def _build_chunk_id(self, page: DocumentPage, chunk_index: int) -> str:
        safe_source = re.sub(r"[^a-zA-Z0-9_.-]+", "_", page.source).strip("_")
        return f"{safe_source}_p{page.page_number}_c{chunk_index}"

    def _read_positive_int(self, name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None or not value.strip():
            return default

        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"{name} must be an integer.") from exc

        if parsed <= 0:
            raise ValueError(f"{name} must be greater than 0.")

        return parsed

    def _read_non_negative_int(self, name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None or not value.strip():
            return default

        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"{name} must be an integer.") from exc

        if parsed < 0:
            raise ValueError(f"{name} cannot be negative.")

        return parsed

