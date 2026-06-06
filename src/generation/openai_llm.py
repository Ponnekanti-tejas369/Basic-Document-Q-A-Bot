"""OpenAI LLM provider."""

from __future__ import annotations

from src.generation.base_llm import BaseLLM
from src.utils.config import get_env

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class OpenAILLM(BaseLLM):
    """Generate grounded answers with the OpenAI API."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or get_env("LLM_MODEL", DEFAULT_OPENAI_MODEL)
        self._api_key = (get_env("OPENAI_API_KEY", "") or "").strip()
        if not self._api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Add it to your .env file."
            )

        self._client = self._create_client()

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You answer questions only from the provided "
                            "retrieved document context."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
        except Exception as exc:
            raise RuntimeError(f"OpenAI answer generation failed: {exc}") from exc

        answer = response.choices[0].message.content or ""
        return answer.strip()

    def _create_client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is required for OpenAI generation. Install it with "
                "`pip install openai`."
            ) from exc

        try:
            return OpenAI(api_key=self._api_key)
        except Exception as exc:
            raise RuntimeError("Failed to initialize OpenAI client.") from exc
