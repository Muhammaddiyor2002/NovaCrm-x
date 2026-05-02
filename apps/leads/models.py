from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TenantOwnedModel


class LeadStatus(models.TextChoices):
    NEW = "new", "New"
    WORKING = "working", "Working"
    QUALIFIED = "qualified", "Qualified"
    DISQUALIFIED = "disqualified", "Disqualified"
    CONVERTED = "converted", "Converted"


class LeadSource(models.TextChoices):
    WEBSITE = "website", "Website"
    REFERRAL = "referral", "Referral"
    AD = "ad", "Advertisement"
    EVENT = "event", "Event"
    IMPORT = "import", "Import"
    API = "api", "API"
    MANUAL = "manual", "Manual"


class Lead(TenantOwnedModel):
    name = models.CharField(max_length=160)
    email = models.EmailField(blank=True, default="", db_index=True)
    phone = models.CharField(max_length=40, blank=True, default="")
    company_name = models.CharField(max_length=200, blank=True, default="")
    source = models.CharField(max_length=16, choices=LeadSource.choices, default=LeadSource.MANUAL)
    status = models.CharField(max_length=16, choices=LeadStatus.choices, default=LeadStatus.NEW)
    score = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_leads",
    )
    notes = models.TextField(blank=True, default="")

    converted_contact = models.ForeignKey(
        "customers.Contact",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="originating_leads",
    )
    converted_deal = models.ForeignKey(
        "deals.Deal",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="originating_leads",
    )

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "score"]),
            models.Index(fields=["tenant", "email"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.name
