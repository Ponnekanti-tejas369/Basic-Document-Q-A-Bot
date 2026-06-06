"""Plain text document loader."""

from __future__ import annotations

from pathlib import Path

from src.loaders.base_loader import BaseDocumentLoader
from src.utils.schemas import DocumentPage
from src.utils.text_cleaning import clean_text


class TXTLoader(BaseDocumentLoader):
    """Extract clean text from TXT files."""

    supported_extensions = (".txt",)

    def load(self, file_path: Path) -> list[DocumentPage]:
        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError(f"Failed to read TXT file {file_path}: {exc}") from exc

        sections = [section for section in raw_text.split("\f") if clean_text(section)]
        if not sections:
            return []

        pages: list[DocumentPage] = []
        for section_index, section in enumerate(sections, start=1):
            text = clean_text(section)
            if not text:
                continue

            pages.append(
                DocumentPage(
                    text=text,
                    source=file_path.name,
                    file_path=str(file_path),
                    file_type="txt",
                    page_number=section_index,
                )
            )

        return pages

