from __future__ import annotations

import pytest

from apps.audit.models import AuditAction, AuditLog
from apps.customers.models import Contact


@pytest.mark.django_db
def test_create_emits_audit_log(tenant, user):
    contact = Contact.objects.create(
        tenant=tenant, first_name="Audit", last_name="Test", email="a@a.com", owner=user
    )
    log = AuditLog.objects.filter(target_object_id=contact.id, action=AuditAction.CREATED).first()
    assert log is not None
    assert log.tenant_id == tenant.id


@pytest.mark.django_db
def test_update_emits_audit_log(tenant, user):
    contact = Contact.objects.create(tenant=tenant, first_name="A", email="a@a.com", owner=user)
    contact.last_name = "Updated"
    contact.save()
    updates = AuditLog.objects.filter(
        target_object_id=contact.id, action=AuditAction.UPDATED
    ).count()
    assert updates >= 1
