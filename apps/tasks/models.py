from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TenantOwnedModel


class TaskStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    DONE = "done", "Done"
    CANCELLED = "cancelled", "Cancelled"


class TaskPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class Task(TenantOwnedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    status = models.CharField(max_length=16, choices=TaskStatus.choices, default=TaskStatus.OPEN)
    priority = models.CharField(
        max_length=8, choices=TaskPriority.choices, default=TaskPriority.NORMAL
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    related_content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.SET_NULL
    )
    related_object_id = models.UUIDField(null=True, blank=True)
    related_to = GenericForeignKey("related_content_type", "related_object_id")

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "status", "due_at"]),
            models.Index(fields=["tenant", "assignee", "status"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title
