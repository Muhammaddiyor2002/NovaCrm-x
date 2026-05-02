"""Make `active_tenant` available to all templates."""

from __future__ import annotations


def active_tenant(request) -> dict:
    return {"active_tenant": getattr(request, "tenant", None)}
