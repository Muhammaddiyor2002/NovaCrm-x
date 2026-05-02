from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TenantOwnedModel


class NotificationLevel(models.TextChoices):
    INFO = "info", "Info"
    SUCCESS = "success", "Success"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"


class Notification(TenantOwnedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    level = models.CharField(
        max_length=10, choices=NotificationLevel.choices, default=NotificationLevel.INFO
    )
    verb = models.CharField(max_length=50)
    message = models.TextField()
    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.SET_NULL
    )
    target_object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "recipient", "read_at"]),
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Notification({self.verb})"
