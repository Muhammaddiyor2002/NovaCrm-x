from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TenantOwnedModel


class TicketStatus(models.TextChoices):
    NEW = "new", "New"
    OPEN = "open", "Open"
    PENDING = "pending", "Pending"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class TicketPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class Ticket(TenantOwnedModel):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    contact = models.ForeignKey(
        "customers.Contact",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    status = models.CharField(max_length=12, choices=TicketStatus.choices, default=TicketStatus.NEW)
    priority = models.CharField(
        max_length=8, choices=TicketPriority.choices, default=TicketPriority.NORMAL
    )
    sla_due_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "status", "priority"]),
            models.Index(fields=["tenant", "assignee", "status"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.subject


class TicketReply(TenantOwnedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ticket_replies",
    )
    body = models.TextField()
    is_internal = models.BooleanField(default=False)

    class Meta(TenantOwnedModel.Meta):
        ordering = ("created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"Reply on {self.ticket_id}"
