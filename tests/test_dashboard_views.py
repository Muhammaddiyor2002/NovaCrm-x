from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
def test_landing_renders():
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"NovaCRM X" in response.content


@pytest.mark.django_db
def test_login_page_renders():
    client = Client()
    response = client.get("/login/")
    assert response.status_code == 200
    assert b"Sign in" in response.content


@pytest.mark.django_db
def test_dashboard_requires_login():
    client = Client()
    response = client.get("/dashboard/")
    assert response.status_code == 302
    assert "/login/" in response["Location"]


@pytest.mark.django_db
def test_dashboard_renders_for_authenticated_user(user, tenant):
    client = Client()
    client.force_login(user)
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"Dashboard" in response.content
