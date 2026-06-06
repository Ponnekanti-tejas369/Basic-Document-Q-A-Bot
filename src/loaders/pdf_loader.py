"""PDF document loader using PyMuPDF."""

from __future__ import annotations

from pathlib import Path

from src.loaders.base_loader import BaseDocumentLoader
from src.utils.schemas import DocumentPage
from src.utils.text_cleaning import clean_text


class PDFLoader(BaseDocumentLoader):
    """Extract clean text from each PDF page."""

    supported_extensions = (".pdf",)

    def load(self, file_path: Path) -> list[DocumentPage]:
        try:
            import fitz
        except ImportError as exc:
            raise ImportError(
                "PyMuPDF is required for PDF loading. Install it with "
                "`pip install PyMuPDF`."
            ) from exc

        pages: list[DocumentPage] = []

        try:
            with fitz.open(file_path) as document:
                for page_index, page in enumerate(document, start=1):
                    text = clean_text(page.get_text("text"))
                    if not text:
                        continue

                    pages.append(
                        DocumentPage(
                            text=text,
                            source=file_path.name,
                            file_path=str(file_path),
                            file_type="pdf",
                            page_number=page_index,
                        )
                    )
        except Exception as exc:
            raise RuntimeError(f"Failed to extract PDF text from {file_path}: {exc}") from exc

        return pages

