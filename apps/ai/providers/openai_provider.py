"""OpenAI-compatible HTTP provider (works with OpenAI, Azure OpenAI, Ollama, vLLM)."""

from __future__ import annotations

import time

import httpx

from .base import BaseAIProvider, CompletionResult


class OpenAIProvider(BaseAIProvider):
    name = "openai"
    timeout = 30.0

    def __init__(self, *, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    # --- Public API ---------------------------------------------------------

    def complete(
        self, *, prompt: str, system: str = "", temperature: float = 0.2
    ) -> CompletionResult:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages, "temperature": temperature}
        t0 = time.monotonic()
        data = self._post("/chat/completions", body)
        latency = int((time.monotonic() - t0) * 1000)
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        return CompletionResult(
            text=text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            latency_ms=latency,
            raw=data,
        )

    def classify(self, *, text: str, labels: list[str]) -> str:
        prompt = (
            f"Classify the following text into one of these labels: {labels}.\n\n"
            f"Text:\n{text}\n\nReply with only the label."
        )
        result = self.complete(prompt=prompt, temperature=0.0)
        answer = result.text.strip().splitlines()[0].strip().strip("`'\"").lower()
        for label in labels:
            if answer == label.lower():
                return label
        return labels[0]

    def score(self, *, text: str, criteria: str) -> int:
        prompt = (
            f"On a scale of 0-100, score the following text against this criteria:\n"
            f"Criteria: {criteria}\n\nText:\n{text}\n\nReply with only the integer."
        )
        result = self.complete(prompt=prompt, temperature=0.0)
        try:
            value = int("".join(c for c in result.text if c.isdigit())[:3])
        except ValueError:
            value = 0
        return max(0, min(100, value))

    # --- Internals ----------------------------------------------------------

    def _post(self, path: str, body: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            return r.json()
