"""Abstract base class for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompletionResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    raw: dict | None = None


class BaseAIProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(
        self, *, prompt: str, system: str = "", temperature: float = 0.2
    ) -> CompletionResult: ...

    @abstractmethod
    def classify(self, *, text: str, labels: list[str]) -> str: ...

    @abstractmethod
    def score(self, *, text: str, criteria: str) -> int:
        """Return a 0-100 score."""
        ...
