"""Thread-local request context.

Used by the tenant middleware to propagate the active tenant and acting user into
queryset managers and audit logging without polluting function signatures across
the codebase.
"""

from __future__ import annotations

import contextvars
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:  # pragma: no cover
    from apps.accounts.models import User
    from apps.tenants.models import Tenant

_active_tenant: contextvars.ContextVar[UUID | None] = contextvars.ContextVar(
    "active_tenant", default=None
)
_active_user: contextvars.ContextVar[UUID | None] = contextvars.ContextVar(
    "active_user", default=None
)
_audit_meta: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "audit_meta", default=None
)


def set_active_tenant(tenant: Tenant | UUID | None) -> None:
    if tenant is None:
        _active_tenant.set(None)
        return
    tenant_id = tenant.id if hasattr(tenant, "id") else tenant
    _active_tenant.set(tenant_id)


def get_active_tenant_id() -> UUID | None:
    return _active_tenant.get()


def set_active_user(user: User | UUID | None) -> None:
    if user is None:
        _active_user.set(None)
        return
    user_id = user.id if hasattr(user, "id") else user
    _active_user.set(user_id)


def get_active_user_id() -> UUID | None:
    return _active_user.get()


def set_audit_meta(meta: dict | None) -> None:
    _audit_meta.set(meta)


def get_audit_meta() -> dict | None:
    return _audit_meta.get()


@contextmanager
def tenant_scope(tenant: Tenant | UUID | None) -> Iterator[None]:
    """Temporarily set the active tenant; useful in Celery tasks and tests."""
    token = _active_tenant.set(tenant.id if hasattr(tenant, "id") else tenant)
    try:
        yield
    finally:
        _active_tenant.reset(token)
