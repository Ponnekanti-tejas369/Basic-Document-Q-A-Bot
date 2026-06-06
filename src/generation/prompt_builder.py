"""Prompt builder for grounded RAG answers."""

from __future__ import annotations

from src.utils import format_citation

INSUFFICIENT_CONTEXT_RESPONSE = (
    "The provided documents do not contain enough information to answer this question."
)


def build_grounded_prompt(
    question: str,
    retrieved_chunks: list[dict[str, object]],
) -> str:
    """Build a context-only answer generation prompt."""

    context_blocks = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk.get("metadata", {})
        citation = format_citation(metadata)
        text = str(chunk.get("text", "")).strip()
        context_blocks.append(
            f"Context chunk {index}\n"
            f"Citation: {citation}\n"
            f"Text:\n{text}"
        )

    context = "\n\n---\n\n".join(context_blocks)

    return f"""You are a document question-answering assistant.

Answer the user's question using only the provided context chunks.
Do not use outside knowledge.
If the context does not contain enough information to answer the question, respond exactly:
"{INSUFFICIENT_CONTEXT_RESPONSE}"

Rules:
- Keep the answer clear and concise.
- Include inline citations using the citation labels from the context.
- Cite sources with source filename and page or section number.
- Do not invent citations.
- Do not mention sources that are not present in the context.

User question:
{question}

Retrieved context:
{context}

Grounded answer:
"""

