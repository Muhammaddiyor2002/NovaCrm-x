from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TenantOwnedModel


class DealStatus(models.TextChoices):
    OPEN = "open", "Open"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class Pipeline(TenantOwnedModel):
    name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        unique_together = ("tenant", "name")
        indexes = [models.Index(fields=["tenant", "is_default"])]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Stage(TenantOwnedModel):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=120)
    position = models.PositiveSmallIntegerField(default=0)
    probability = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    class Meta(TenantOwnedModel.Meta):
        ordering = ("pipeline", "position")
        indexes = [models.Index(fields=["pipeline", "position"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.pipeline.name} / {self.name}"


class Deal(TenantOwnedModel):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.PROTECT, related_name="deals")
    stage = models.ForeignKey(Stage, on_delete=models.PROTECT, related_name="deals")
    title = models.CharField(max_length=200)
    company = models.ForeignKey(
        "customers.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deals",
    )
    primary_contact = models.ForeignKey(
        "customers.Contact",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deals",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_deals",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    probability = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    expected_close_date = models.DateField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=DealStatus.choices, default=DealStatus.OPEN)
    lost_reason = models.CharField(max_length=120, blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "stage"]),
            models.Index(fields=["tenant", "owner"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    @property
    def weighted_amount(self):
        return (self.amount or 0) * (self.probability or 0) / 100
