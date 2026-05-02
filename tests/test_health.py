from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_healthz(anon_client):
    response = anon_client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
