from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel, TenantOwnedModel


class PlanInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class Plan(BaseModel):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_users = models.PositiveIntegerField(null=True, blank=True)
    max_contacts = models.PositiveIntegerField(null=True, blank=True)
    features = models.JSONField(default=dict, blank=True)
    stripe_price_id_monthly = models.CharField(max_length=64, blank=True, default="")
    stripe_price_id_yearly = models.CharField(max_length=64, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("price_monthly",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class SubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", "Trialing"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past Due"
    CANCELED = "canceled", "Canceled"
    UNPAID = "unpaid", "Unpaid"


class Subscription(TenantOwnedModel):
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    interval = models.CharField(
        max_length=10, choices=PlanInterval.choices, default=PlanInterval.MONTHLY
    )
    status = models.CharField(
        max_length=12, choices=SubscriptionStatus.choices, default=SubscriptionStatus.TRIALING
    )
    started_at = models.DateTimeField(auto_now_add=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=64, blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        unique_together = ("tenant", "plan")
        indexes = [models.Index(fields=["tenant", "status"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.tenant_id} → {self.plan.code} ({self.status})"


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    OPEN = "open", "Open"
    PAID = "paid", "Paid"
    UNCOLLECTIBLE = "uncollectible", "Uncollectible"
    VOID = "void", "Void"


class Invoice(TenantOwnedModel):
    subscription = models.ForeignKey(
        Subscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices"
    )
    number = models.CharField(max_length=64, blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=14, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    stripe_invoice_id = models.CharField(max_length=64, blank=True, default="")
    pdf_url = models.URLField(blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        ordering = ("-issued_at", "-created_at")
        indexes = [models.Index(fields=["tenant", "status"])]
