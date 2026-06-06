"""DOCX document loader using python-docx."""

from __future__ import annotations

from pathlib import Path

from src.loaders.base_loader import BaseDocumentLoader
from src.utils.schemas import DocumentPage
from src.utils.text_cleaning import clean_text


class DOCXLoader(BaseDocumentLoader):
    """Extract clean text from DOCX paragraphs grouped by heading sections."""

    supported_extensions = (".docx",)

    def load(self, file_path: Path) -> list[DocumentPage]:
        try:
            from docx import Document
        except ImportError as exc:
            raise ImportError(
                "python-docx is required for DOCX loading. Install it with "
                "`pip install python-docx`."
            ) from exc

        try:
            document = Document(file_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to open DOCX file {file_path}: {exc}") from exc

        sections = self._paragraphs_to_sections(document.paragraphs)
        pages: list[DocumentPage] = []

        for section_index, section_text in enumerate(sections, start=1):
            text = clean_text(section_text)
            if not text:
                continue

            pages.append(
                DocumentPage(
                    text=text,
                    source=file_path.name,
                    file_path=str(file_path),
                    file_type="docx",
                    page_number=section_index,
                )
            )

        return pages

    def _paragraphs_to_sections(self, paragraphs: object) -> list[str]:
        sections: list[str] = []
        current_section: list[str] = []

        for paragraph in paragraphs:
            text = clean_text(paragraph.text)
            if not text:
                continue

            style_name = getattr(paragraph.style, "name", "")
            is_heading = style_name.lower().startswith("heading")

            if is_heading and current_section:
                sections.append("\n".join(current_section))
                current_section = [text]
            else:
                current_section.append(text)

        if current_section:
            sections.append("\n".join(current_section))

        return sections

