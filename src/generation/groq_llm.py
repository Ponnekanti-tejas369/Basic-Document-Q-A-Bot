"""Groq LLM provider."""

from __future__ import annotations

from src.generation.base_llm import BaseLLM
from src.utils.config import get_env

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


class GroqLLM(BaseLLM):
    """Generate grounded answers with the Groq API."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or get_env("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        self._api_key = (get_env("GROQ_API_KEY", "") or "").strip()
        if not self._api_key:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER=groq. "
                "Add it to your .env file."
            )

        self._client = self._create_client()

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        try:
            completion = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        except Exception as exc:
            raise RuntimeError(f"Groq answer generation failed: {exc}") from exc

        answer = completion.choices[0].message.content or ""
        return answer.strip()

    def _create_client(self):
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "groq is required for Groq generation. Install it with "
                "`pip install groq`."
            ) from exc

        try:
            return Groq(api_key=self._api_key)
        except Exception as exc:
            raise RuntimeError("Failed to initialize Groq client.") from exc
