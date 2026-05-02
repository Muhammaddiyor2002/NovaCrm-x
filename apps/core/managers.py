"""Custom managers and querysets for tenant-aware soft-deletable models."""

from __future__ import annotations

from django.db import models

from .context import get_active_tenant_id


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that hides soft-deleted rows by default."""

    def alive(self) -> SoftDeleteQuerySet:
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> SoftDeleteQuerySet:
        return self.filter(deleted_at__isnull=False)

    def delete(self):  # type: ignore[override]
        from django.utils import timezone

        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class TenantQuerySet(SoftDeleteQuerySet):
    """QuerySet that auto-filters by the active tenant when one is set."""

    def for_active_tenant(self) -> TenantQuerySet:
        tenant_id = get_active_tenant_id()
        if tenant_id is None:
            return self.none()
        return self.filter(tenant_id=tenant_id)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):  # type: ignore[misc]
    """Default manager: returns alive rows only."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().alive()


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):  # type: ignore[misc]
    """Manager that exposes soft-deleted rows as well."""


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):  # type: ignore[misc]
    """Default manager for tenant-owned models. Auto-scopes to the active tenant."""

    def get_queryset(self) -> TenantQuerySet:
        qs = super().get_queryset().alive()
        tenant_id = get_active_tenant_id()
        if tenant_id is None:
            return qs
        return qs.filter(tenant_id=tenant_id)


class CrossTenantManager(models.Manager.from_queryset(TenantQuerySet)):  # type: ignore[misc]
    """Escape hatch for super-admin / system queries that span tenants."""

    def get_queryset(self) -> TenantQuerySet:
        return super().get_queryset()
