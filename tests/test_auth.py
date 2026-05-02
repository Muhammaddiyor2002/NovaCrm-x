from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_register_creates_user_and_tenant(anon_client, system_roles):
    response = anon_client.post(
        "/api/v1/auth/register/",
        {
            "email": "bob@example.com",
            "full_name": "Bob",
            "password": "supersecret9!",
            "tenant_name": "Bob's Inc.",
        },
        format="json",
    )
    assert response.status_code == 201, response.content
    data = response.json()
    assert data["email"] == "bob@example.com"

    # Login should work
    login = anon_client.post(
        "/api/v1/auth/login/",
        {"email": "bob@example.com", "password": "supersecret9!"},
        format="json",
    )
    assert login.status_code == 200
    assert "access" in login.json()


@pytest.mark.django_db
def test_me_endpoint_requires_auth(anon_client):
    response = anon_client.get("/api/v1/auth/me/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_me_endpoint_returns_user(auth_client, user):
    response = auth_client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.json()["email"] == user.email
