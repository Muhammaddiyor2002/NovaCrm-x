"""Base abstract models shared across the project."""

from __future__ import annotations

import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from .managers import (
    AllObjectsManager,
    CrossTenantManager,
    SoftDeleteManager,
    TenantManager,
)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class BaseModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Reusable base for ANY model — UUID PK, timestamps, soft delete."""

    class Meta:
        abstract = True


class TenantOwnedModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Abstract base for tenant-scoped business models.

    Concrete subclasses must NOT redeclare `tenant`; this FK provides it. The
    default manager auto-filters to the active tenant pulled from the request
    context. Use `all_tenants` for super-admin queries.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="+",
        db_index=True,
    )

    objects = TenantManager()
    all_tenants = CrossTenantManager()

    class Meta:
        abstract = True
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["tenant", "created_at"])]


class Note(TenantOwnedModel):
    """Generic note attachable to any tenant-owned object."""

    author = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="authored_notes"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    target = GenericForeignKey("content_type", "object_id")
    body = models.TextField()

    class Meta(TenantOwnedModel.Meta):
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        indexes = [
            models.Index(fields=["tenant", "content_type", "object_id"]),
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        snippet = (self.body or "")[:40]
        return f"Note({snippet!r})"
