"""DRF permission classes that enforce tenant + RBAC checks."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.core.context import set_active_tenant, set_active_user
from apps.tenants.middleware import resolve_tenant
from apps.tenants.models import Membership


def _ensure_tenant(request):
    """Re-run tenant resolution after DRF auth has populated ``request.user``."""
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        # Force re-resolution since DRF/JWT auth ran after middleware.
        request._tenant_resolved = None  # type: ignore[attr-defined]
        tenant = resolve_tenant(request)
    if tenant is not None:
        set_active_tenant(tenant)
        if request.user.is_authenticated:
            set_active_user(request.user)
    return tenant


class IsTenantMember(BasePermission):
    """Allow only authenticated users that belong to the active tenant."""

    message = "You don't have access to this workspace."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        tenant = _ensure_tenant(request)
        if tenant is None:
            return False
        return Membership.objects.filter(user=request.user, tenant=tenant).exists()


class HasPermissionCode(BasePermission):
    """Require a specific permission code declared by the view as `required_permission`."""

    def has_permission(self, request, view) -> bool:
        required = getattr(view, "required_permission", None)
        if required is None:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        tenant = _ensure_tenant(request)
        if tenant is None:
            return False
        membership = (
            Membership.objects.filter(user=request.user, tenant=tenant)
            .select_related("role")
            .first()
        )
        if not membership:
            return False
        return membership.role.has_permission(required)


class IsObjectInTenant(BasePermission):
    """Defense-in-depth: ensure the object belongs to the request's tenant."""

    def has_object_permission(self, request, view, obj) -> bool:
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return False
        obj_tenant_id = getattr(obj, "tenant_id", None)
        return obj_tenant_id == tenant.id
