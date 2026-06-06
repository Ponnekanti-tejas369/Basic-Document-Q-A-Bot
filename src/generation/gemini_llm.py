"""Google Gemini LLM provider."""

from __future__ import annotations

from src.generation.base_llm import BaseLLM
from src.utils.config import get_env

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiLLM(BaseLLM):
    """Generate grounded answers with the Gemini API."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or get_env("LLM_MODEL", DEFAULT_GEMINI_MODEL)
        self._api_key = (get_env("GOOGLE_API_KEY", "") or "").strip()
        if not self._api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when LLM_PROVIDER=gemini. "
                "Add it to your .env file."
            )

        self._client = self._create_client()

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini answer generation failed: {exc}") from exc

        answer = getattr(response, "text", "") or ""
        return answer.strip()

    def _create_client(self):
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for Gemini generation. "
                "Install it with `pip install google-genai`."
            ) from exc

        try:
            return genai.Client(api_key=self._api_key)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize Gemini client for model "
                f"'{self._model_name}': {exc}"
            ) from exc
