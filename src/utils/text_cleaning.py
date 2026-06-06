"""Text normalization helpers used by document loaders."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Normalize whitespace while keeping paragraph breaks readable."""

    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()

