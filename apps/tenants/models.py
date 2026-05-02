"""Multi-tenant primitives: Tenant + Membership."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import BaseModel


class TenantStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    ARCHIVED = "archived", "Archived"


class Tenant(BaseModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=64, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_tenants",
    )
    status = models.CharField(
        max_length=16, choices=TenantStatus.choices, default=TenantStatus.ACTIVE
    )
    plan = models.ForeignKey(
        "billing.Plan",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tenants",
    )
    stripe_customer_id = models.CharField(max_length=64, blank=True, default="")
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    settings_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["status"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.slug})"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.name) or "tenant"
            slug = base
            i = 1
            while Tenant.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_in_trial(self) -> bool:
        return bool(self.trial_ends_at and self.trial_ends_at > timezone.now())


class Membership(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey("rbac.Role", on_delete=models.PROTECT, related_name="memberships")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invites",
    )
    joined_at = models.DateTimeField(default=timezone.now)
    is_default = models.BooleanField(
        default=False,
        help_text="Tenant the user lands on after login when they belong to multiple.",
    )

    class Meta:
        unique_together = ("user", "tenant")
        ordering = ("-joined_at",)
        indexes = [
            models.Index(fields=["tenant", "user"]),
            models.Index(fields=["user", "is_default"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} @ {self.tenant} ({self.role.name})"
