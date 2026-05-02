"""Resolve the active tenant for each request.

DRF authenticates inside the view, so the user is typically still
``AnonymousUser`` at middleware time. To handle both classic Django views
(login/session) and DRF/JWT views, this middleware does an initial best-effort
resolution and exposes a lazy ``resolve_tenant(request)`` helper that any
permission class / view can call after authentication has settled.
"""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from apps.core.context import set_active_tenant, set_active_user

from .models import Membership, Tenant


def resolve_tenant(request: HttpRequest) -> Tenant | None:
    """Return (and cache) the tenant for this request.

    Resolution order:
      1. ``request._tenant_resolved`` — already computed for this request.
      2. Subdomain / membership rules.
    """
    cached = getattr(request, "_tenant_resolved", None)
    if cached is not None:
        return cached

    strategy = getattr(settings, "TENANT_RESOLUTION", "membership")
    if strategy == "subdomain":
        tenant = _by_subdomain(request)
    else:
        tenant = _by_membership(request)

    request._tenant_resolved = tenant  # type: ignore[attr-defined]
    request.tenant = tenant  # type: ignore[attr-defined]
    set_active_tenant(tenant)
    set_active_user(
        request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    )
    return tenant


def _by_subdomain(request: HttpRequest) -> Tenant | None:
    host = request.get_host().split(":")[0]
    parts = host.split(".")
    if len(parts) < 3:
        return None
    return Tenant.objects.filter(slug=parts[0], status="active").first()


def _by_membership(request: HttpRequest) -> Tenant | None:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None

    explicit_id = request.headers.get("X-Tenant-Id")
    if explicit_id:
        membership = Membership.objects.filter(user=user, tenant_id=explicit_id).first()
        if membership:
            return membership.tenant

    membership = (
        Membership.objects.filter(user=user)
        .order_by("-is_default", "-joined_at")
        .select_related("tenant")
        .first()
    )
    return membership.tenant if membership else None


class TenantMiddleware(MiddlewareMixin):
    """Attach ``request.tenant`` early; permission classes refresh it later."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        request._tenant_resolved = None  # type: ignore[attr-defined]
        request.tenant = None  # type: ignore[attr-defined]
        # Best-effort early resolution (subdomain works without auth).
        resolve_tenant(request)
        return None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        set_active_tenant(None)
        set_active_user(None)
        return response
