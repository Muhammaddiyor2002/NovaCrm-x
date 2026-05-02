from __future__ import annotations

from apps.ai.providers import get_provider


def analyze_sentiment(text: str) -> str:
    """Return one of 'positive', 'neutral', 'negative'."""
    return get_provider().classify(text=text, labels=["positive", "neutral", "negative"])
