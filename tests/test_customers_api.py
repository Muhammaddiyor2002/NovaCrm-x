from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_create_and_list_contact(auth_client, tenant):
    response = auth_client.post(
        "/api/v1/customers/contacts/",
        {"first_name": "Carol", "last_name": "Smith", "email": "carol@example.com"},
        format="json",
    )
    assert response.status_code == 201, response.content

    listing = auth_client.get("/api/v1/customers/contacts/")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["results"][0]["email"] == "carol@example.com"


@pytest.mark.django_db
def test_unauthenticated_cannot_list(anon_client):
    response = anon_client.get("/api/v1/customers/contacts/")
    assert response.status_code in (401, 403)
