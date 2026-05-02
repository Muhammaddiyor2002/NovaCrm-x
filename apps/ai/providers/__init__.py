from __future__ import annotations

from django.conf import settings

from .base import BaseAIProvider
from .dummy import DummyProvider
from .openai_provider import OpenAIProvider


def get_provider() -> BaseAIProvider:
    """Return the configured AI provider instance."""
    name = getattr(settings, "AI_PROVIDER", "dummy")
    if name == "openai":
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
        )
    if name == "local":
        # Local LLM speaks the OpenAI HTTP protocol (e.g. Ollama, vLLM).
        return OpenAIProvider(
            api_key="local",
            base_url=settings.LOCAL_LLM_BASE_URL,
            model=settings.LOCAL_LLM_MODEL,
        )
    return DummyProvider()


__all__ = ["BaseAIProvider", "DummyProvider", "OpenAIProvider", "get_provider"]
