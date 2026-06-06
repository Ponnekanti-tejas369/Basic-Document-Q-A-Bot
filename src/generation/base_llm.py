"""Base interface for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Interface implemented by answer generation providers."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the LLM model in use."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from a complete prompt."""

