"""Business services for tenant onboarding."""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.rbac.models import Role
from apps.rbac.seed import ensure_system_roles

from .models import Membership, Tenant


@transaction.atomic
def bootstrap_tenant_for_user(*, user, tenant_name: str) -> Tenant:
    """Create a tenant + owner membership for a freshly-registered user.

    Idempotent in the sense that if the user already owns a tenant we do nothing.
    """
    existing = Tenant.objects.filter(owner=user).first()
    if existing:
        return existing

    ensure_system_roles()
    tenant = Tenant.objects.create(
        name=tenant_name,
        owner=user,
        trial_ends_at=timezone.now()
        + timedelta(days=getattr(settings, "DEFAULT_TENANT_TRIAL_DAYS", 14)),
    )
    owner_role = Role.objects.get(slug="tenant_owner", tenant__isnull=True)
    Membership.objects.create(
        user=user, tenant=tenant, role=owner_role, is_default=True, invited_by=None
    )
    return tenant
