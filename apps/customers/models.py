"""Customers: Companies + Contacts."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TenantOwnedModel


class CompanySize(models.TextChoices):
    SMB = "smb", "1–50"
    MID = "mid", "51–500"
    ENTERPRISE = "enterprise", "501+"


class Company(TenantOwnedModel):
    name = models.CharField(max_length=200, db_index=True)
    website = models.URLField(blank=True, default="")
    industry = models.CharField(max_length=80, blank=True, default="")
    size = models.CharField(max_length=16, choices=CompanySize.choices, blank=True, default="")
    annual_revenue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    address = models.JSONField(default=dict, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_companies",
    )

    class Meta(TenantOwnedModel.Meta):
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=["tenant", "name"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Contact(TenantOwnedModel):
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts"
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True, default="")
    email = models.EmailField(blank=True, default="", db_index=True)
    phone = models.CharField(max_length=40, blank=True, default="")
    title = models.CharField(max_length=120, blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_contacts",
    )
    tags = models.JSONField(default=list, blank=True)

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "email"]),
            models.Index(fields=["tenant", "last_name", "first_name"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
