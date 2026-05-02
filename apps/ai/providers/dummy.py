"""Deterministic dummy provider used in tests and when no API key is set."""

from __future__ import annotations

import hashlib

from .base import BaseAIProvider, CompletionResult


class DummyProvider(BaseAIProvider):
    name = "dummy"

    def complete(
        self, *, prompt: str, system: str = "", temperature: float = 0.2
    ) -> CompletionResult:
        text = "[dummy provider] " + (system + "\n" if system else "") + prompt[:200]
        return CompletionResult(
            text=text,
            prompt_tokens=len(prompt.split()),
            completion_tokens=min(40, len(prompt.split())),
            latency_ms=1,
        )

    def classify(self, *, text: str, labels: list[str]) -> str:
        if not labels:
            return ""
        digest = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        return labels[digest % len(labels)]

    def score(self, *, text: str, criteria: str) -> int:
        # Stable pseudo-score.
        digest = int(hashlib.sha256((text + criteria).encode()).hexdigest(), 16)
        return digest % 101  # 0..100
