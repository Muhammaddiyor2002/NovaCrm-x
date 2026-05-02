"""Smoke tests for the public surface of the app."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/healthz",
        "/api/v1/schema/",
        "/api/v1/docs/",
        "/api/v1/redoc/",
    ],
)
def test_public_endpoints_render(url):
    client = APIClient()
    response = client.get(url)
    assert response.status_code == 200, f"{url} returned {response.status_code}"


def test_swagger_url_name_is_namespaced():
    """drf-spectacular Swagger view must use the namespaced schema URL.

    Regression test: the project includes API URLs under a ``v1`` namespace,
    so the Swagger/Redoc views need ``url_name='v1:schema'`` rather than the
    default ``'schema'``. Without this, hitting /api/v1/docs/ raises
    NoReverseMatch and returns a 500.
    """
    # Make sure the Django reverse for the namespaced schema works.
    assert reverse("v1:schema") == "/api/v1/schema/"
