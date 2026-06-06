"""Local tests for query source citation display helpers."""

from __future__ import annotations

from dataclasses import dataclass

from query import deduplicate_sources, extract_source_info
from src.utils import format_citation


@dataclass
class ObjectResult:
    metadata: dict[str, object]


def test_extract_source_info_from_metadata_dict() -> None:
    result = {
        "metadata": {
            "source": "A Top 60 Claude Skills, Workflows, and GitHub Repos.pdf",
            "page_number": 2,
            "chunk_index": 0,
        }
    }

    source = extract_source_info(result)

    assert format_citation(source) == (
        "[source: A Top 60 Claude Skills, Workflows, and GitHub Repos.pdf, "
        "page/section: 2, chunk: 0]"
    )


def test_extract_source_info_from_top_level_fields() -> None:
    result = {
        "source": "AI Fresher Project kit 2026.pdf",
        "page_number": 5,
        "chunk_index": 0,
    }

    source = extract_source_info(result)

    assert format_citation(source) == (
        "[source: AI Fresher Project kit 2026.pdf, page/section: 5, chunk: 0]"
    )


def test_extract_source_info_from_object_attributes() -> None:
    result = ObjectResult(
        metadata={
            "source": "Perplexity Models.pdf",
            "page_number": 1,
            "chunk_index": 3,
        }
    )

    source = extract_source_info(result)

    assert format_citation(source) == (
        "[source: Perplexity Models.pdf, page/section: 1, chunk: 3]"
    )


def test_deduplicate_sources_removes_repeated_citations() -> None:
    results = [
        {
            "metadata": {
                "source": "AI Fresher Project kit 2026.pdf",
                "page_number": 5,
                "chunk_index": 0,
            }
        },
        {
            "source": "AI Fresher Project kit 2026.pdf",
            "page_number": 5,
            "chunk_index": 0,
        },
        {
            "source": "Claude Code.pdf",
            "page_number": 2,
            "chunk_index": 1,
        },
    ]

    sources = deduplicate_sources(results)

    assert len(sources) == 2
    assert format_citation(sources[0]) == (
        "[source: AI Fresher Project kit 2026.pdf, page/section: 5, chunk: 0]"
    )
    assert format_citation(sources[1]) == (
        "[source: Claude Code.pdf, page/section: 2, chunk: 1]"
    )

