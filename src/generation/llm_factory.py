"""Factory for LLM providers."""

from __future__ import annotations

from src.generation.base_llm import BaseLLM
from src.generation.gemini_llm import GeminiLLM
from src.generation.groq_llm import GroqLLM
from src.generation.openai_llm import OpenAILLM
from src.utils.config import get_llm_provider


def create_llm() -> BaseLLM:
    """Create the configured LLM provider."""

    provider = get_llm_provider()

    if provider == "gemini":
        return GeminiLLM()

    if provider == "openai":
        return OpenAILLM()

    if provider == "groq":
        return GroqLLM()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. Use one of: gemini, openai, groq."
    )
