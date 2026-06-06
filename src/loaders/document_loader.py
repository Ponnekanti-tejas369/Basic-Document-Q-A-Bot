"""Coordinator for loading supported documents from the data directory."""

from __future__ import annotations

import warnings
from pathlib import Path

from src.loaders.base_loader import BaseDocumentLoader
from src.loaders.docx_loader import DOCXLoader
from src.loaders.pdf_loader import PDFLoader
from src.loaders.txt_loader import TXTLoader
from src.utils.schemas import DocumentPage


class DocumentLoader:
    """Load all supported documents from a local data directory."""

    def __init__(
        self,
        data_dir: str | Path = "data",
        loaders: list[BaseDocumentLoader] | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.loaders = loaders or [PDFLoader(), TXTLoader(), DOCXLoader()]

    def list_files(self) -> list[Path]:
        self._validate_data_dir()
        return sorted(
            path
            for path in self.data_dir.iterdir()
            if path.is_file() and not path.name.startswith(".")
        )

    def load_documents(self) -> list[DocumentPage]:
        files = self.list_files()

        if not files:
            raise FileNotFoundError(
                f"No documents found in {self.data_dir}. Add 4 to 5 files, "
                "including at least one PDF."
            )

        if not any(path.suffix.lower() == ".pdf" for path in files):
            raise ValueError(
                f"No PDF found in {self.data_dir}. The assignment requires at "
                "least one PDF document."
            )

        pages: list[DocumentPage] = []

        for file_path in files:
            loader = self._get_loader(file_path)
            if loader is None:
                warnings.warn(
                    f"Skipping unsupported file type: {file_path.name}",
                    stacklevel=2,
                )
                continue

            try:
                extracted_pages = loader.load(file_path)
            except Exception as exc:
                warnings.warn(
                    f"Skipping {file_path.name} because extraction failed: {exc}",
                    stacklevel=2,
                )
                continue

            if not extracted_pages:
                warnings.warn(
                    f"Skipping {file_path.name} because no text was extracted.",
                    stacklevel=2,
                )
                continue

            pages.extend(extracted_pages)

        if not pages:
            raise RuntimeError(
                "No text could be extracted from the supported documents in "
                f"{self.data_dir}."
            )

        return pages

    def _validate_data_dir(self) -> None:
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Data folder not found: {self.data_dir}. Create it and add "
                "4 to 5 local documents."
            )

        if not self.data_dir.is_dir():
            raise NotADirectoryError(f"Data path is not a folder: {self.data_dir}")

    def _get_loader(self, file_path: Path) -> BaseDocumentLoader | None:
        for loader in self.loaders:
            if loader.can_load(file_path):
                return loader

        return None

