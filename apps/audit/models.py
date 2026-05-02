from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TenantOwnedModel


class AuditAction(models.TextChoices):
    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    DELETED = "deleted", "Deleted"
    RESTORED = "restored", "Restored"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"


class AuditLog(TenantOwnedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=16, choices=AuditAction.choices)
    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.SET_NULL
    )
    target_object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["tenant", "action"]),
            models.Index(fields=["tenant", "target_content_type", "target_object_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.action} by {self.actor_id}"
