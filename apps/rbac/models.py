"""Role / Permission models for tenant-scoped RBAC."""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class Permission(BaseModel):
    """Granular permission code, e.g. `customers.view`, `deals.update`, `*`."""

    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.code


class Role(BaseModel):
    """A named bundle of permissions.

    A `tenant=None` role is a system role available to every tenant. A role with
    `tenant != None` is a custom role visible only to that tenant.
    """

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    tenant = models.ForeignKey(
        "tenants.Tenant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="custom_roles",
    )
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    is_system = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = ("tenant", "slug")
        ordering = ("name",)
        indexes = [models.Index(fields=["tenant", "slug"])]

    def __str__(self) -> str:  # pragma: no cover
        scope = "system" if self.is_system else (self.tenant.slug if self.tenant else "?")
        return f"{self.name} [{scope}]"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def has_permission(self, code: str) -> bool:
        codes = set(self.permissions.values_list("code", flat=True))
        if "*" in codes:
            return True
        if code in codes:
            return True
        # Wildcard prefix: e.g. "customers.*" matches "customers.view"
        prefix = code.split(".")[0] + ".*"
        return prefix in codes
