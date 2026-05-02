from __future__ import annotations

import pytest

from apps.ai.providers import get_provider
from apps.ai.providers.dummy import DummyProvider


def test_dummy_provider_is_default():
    provider = get_provider()
    assert isinstance(provider, DummyProvider)


def test_dummy_classify_is_deterministic():
    provider = get_provider()
    a = provider.classify(text="hello world", labels=["positive", "neutral", "negative"])
    b = provider.classify(text="hello world", labels=["positive", "neutral", "negative"])
    assert a == b
    assert a in {"positive", "neutral", "negative"}


def test_dummy_score_in_range():
    provider = get_provider()
    score = provider.score(text="ok", criteria="quality")
    assert 0 <= score <= 100


@pytest.mark.django_db
def test_sentiment_endpoint_requires_auth(anon_client):
    response = anon_client.post("/api/v1/ai/sentiment/", {"text": "great product"}, format="json")
    assert response.status_code in (401, 403)
