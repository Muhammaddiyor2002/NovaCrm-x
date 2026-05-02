from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.core.context import tenant_scope
from apps.customers.models import Contact
from apps.rbac.models import Role
from apps.tenants.models import Membership, Tenant


@pytest.mark.django_db
def test_default_manager_scopes_by_active_tenant(system_roles):
    User = get_user_model()
    owner_a = User.objects.create_user(email="a@example.com", password="x", full_name="A")
    owner_b = User.objects.create_user(email="b@example.com", password="x", full_name="B")
    role = Role.objects.get(slug="tenant_owner", tenant__isnull=True)
    t_a = Tenant.objects.create(name="A Inc", owner=owner_a)
    t_b = Tenant.objects.create(name="B Inc", owner=owner_b)
    Membership.objects.create(user=owner_a, tenant=t_a, role=role, is_default=True)
    Membership.objects.create(user=owner_b, tenant=t_b, role=role, is_default=True)

    Contact.objects.create(tenant=t_a, first_name="Alice", email="alice@a.com")
    Contact.objects.create(tenant=t_b, first_name="Bob", email="bob@b.com")

    with tenant_scope(t_a):
        emails = list(Contact.objects.values_list("email", flat=True))
    assert emails == ["alice@a.com"]

    with tenant_scope(t_b):
        emails = list(Contact.objects.values_list("email", flat=True))
    assert emails == ["bob@b.com"]

    # all_tenants ignores scoping
    assert Contact.all_tenants.count() == 2


@pytest.mark.django_db
def test_membership_middleware_sets_request_tenant(auth_client, user, tenant):
    # Just hitting an authenticated endpoint should resolve the tenant.
    response = auth_client.get("/api/v1/tenants/tenants/me/")
    assert response.status_code == 200
    assert response.json()["id"] == str(tenant.id)
