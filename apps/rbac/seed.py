"""Idempotent seeding of system roles and permissions."""

from __future__ import annotations

from django.db import transaction

from .models import Permission, Role

# Role definitions:    slug → (display name, list of permission codes)
SYSTEM_ROLES: dict[str, tuple[str, list[str]]] = {
    "super_admin": ("Super Admin", ["*"]),
    "tenant_owner": (
        "Tenant Owner",
        [
            "tenant.manage",
            "billing.manage",
            "members.manage",
            "customers.*",
            "leads.*",
            "deals.*",
            "tasks.*",
            "tickets.*",
            "notes.*",
            "ai.*",
        ],
    ),
    "manager": (
        "Manager",
        [
            "customers.*",
            "leads.*",
            "deals.*",
            "tasks.*",
            "tickets.*",
            "notes.*",
            "ai.use",
        ],
    ),
    "sales_rep": (
        "Sales Rep",
        [
            "customers.view",
            "customers.update",
            "leads.*",
            "deals.*",
            "tasks.*",
            "notes.create",
            "notes.view",
            "ai.use",
        ],
    ),
    "support_agent": (
        "Support Agent",
        [
            "customers.view",
            "tickets.*",
            "notes.*",
            "ai.use",
        ],
    ),
    "accountant": (
        "Accountant",
        [
            "billing.*",
            "invoices.*",
            "customers.view",
        ],
    ),
    "read_only": (
        "Read Only",
        [
            "customers.view",
            "leads.view",
            "deals.view",
            "tasks.view",
            "tickets.view",
            "notes.view",
        ],
    ),
}


@transaction.atomic
def ensure_system_roles() -> None:
    # Permissions are created on demand.
    all_codes = {code for _, codes in SYSTEM_ROLES.values() for code in codes}
    code_to_perm = {}
    for code in all_codes:
        perm, _ = Permission.objects.get_or_create(code=code)
        code_to_perm[code] = perm

    for slug, (name, codes) in SYSTEM_ROLES.items():
        role, _ = Role.objects.get_or_create(
            slug=slug,
            tenant=None,
            defaults={"name": name, "is_system": True, "description": f"System role: {name}"},
        )
        role.is_system = True
        role.name = name
        role.save(update_fields=["is_system", "name"])
        role.permissions.set([code_to_perm[c] for c in codes])
