"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.core.context import set_active_tenant
from apps.rbac.models import Role
from apps.rbac.seed import ensure_system_roles
from apps.tenants.models import Membership, Tenant


@pytest.fixture(autouse=True)
def _reset_active_tenant():
    yield
    set_active_tenant(None)


@pytest.fixture
def system_roles(db):
    ensure_system_roles()


@pytest.fixture
def user(db, system_roles):
    User = get_user_model()
    return User.objects.create_user(
        email="alice@example.com", password="secret123", full_name="Alice"
    )


@pytest.fixture
def tenant(db, user, system_roles):
    t = Tenant.objects.create(
        name="Acme",
        owner=user,
        trial_ends_at=timezone.now() + timedelta(days=14),
    )
    role = Role.objects.get(slug="tenant_owner", tenant__isnull=True)
    Membership.objects.create(user=user, tenant=t, role=role, is_default=True)
    return t


@pytest.fixture
def auth_client(user, tenant) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    client.defaults["HTTP_X_TENANT_ID"] = str(tenant.id)
    return client


@pytest.fixture
def anon_client() -> APIClient:
    return APIClient()
