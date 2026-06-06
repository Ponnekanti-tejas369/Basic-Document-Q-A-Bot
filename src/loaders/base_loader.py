"""Base interface for document loaders."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.utils.schemas import DocumentPage


class BaseDocumentLoader(ABC):
    """Interface implemented by all document format loaders."""

    supported_extensions: tuple[str, ...] = ()

    def can_load(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def load(self, file_path: Path) -> list[DocumentPage]:
        """Extract document pages or sections from a file."""

