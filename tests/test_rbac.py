from __future__ import annotations

import pytest

from apps.rbac.models import Role


@pytest.mark.django_db
def test_role_has_permission_wildcards(system_roles):
    super_admin = Role.objects.get(slug="super_admin", tenant__isnull=True)
    assert super_admin.has_permission("anything.you.want")

    sales_rep = Role.objects.get(slug="sales_rep", tenant__isnull=True)
    assert sales_rep.has_permission("leads.update")
    assert sales_rep.has_permission("customers.view")
    assert not sales_rep.has_permission("billing.manage")


@pytest.mark.django_db
def test_read_only_can_only_view(system_roles):
    role = Role.objects.get(slug="read_only", tenant__isnull=True)
    assert role.has_permission("customers.view")
    assert not role.has_permission("customers.update")
    assert not role.has_permission("leads.update")
