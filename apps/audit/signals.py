"""Signals that auto-create AuditLog rows for tenant-owned models."""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.context import get_active_user_id, get_audit_meta
from apps.core.models import TenantOwnedModel

from .models import AuditAction, AuditLog


def _serializable_field_value(value):
    """Coerce model field values to something JSON-friendly."""
    if value is None or isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)


def _capture_state(instance) -> dict:
    data = {}
    for field in instance._meta.concrete_fields:
        if field.name in {"id", "tenant", "created_at", "updated_at", "deleted_at"}:
            continue
        try:
            data[field.name] = _serializable_field_value(getattr(instance, field.name))
        except Exception:
            continue
    return data


@receiver(post_save)
def _on_save(sender, instance, created, **kwargs) -> None:
    if not isinstance(instance, TenantOwnedModel):
        return
    if sender.__name__ == "AuditLog":  # never recurse
        return
    meta = get_audit_meta() or {}
    AuditLog.objects.create(
        tenant=instance.tenant,
        actor_id=get_active_user_id(),
        action=AuditAction.CREATED if created else AuditAction.UPDATED,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        changes=_capture_state(instance),
        ip_address=meta.get("ip"),
        user_agent=meta.get("user_agent", ""),
    )


@receiver(post_delete)
def _on_delete(sender, instance, **kwargs) -> None:
    if not isinstance(instance, TenantOwnedModel):
        return
    if sender.__name__ == "AuditLog":
        return
    meta = get_audit_meta() or {}
    AuditLog.objects.create(
        tenant=instance.tenant,
        actor_id=get_active_user_id(),
        action=AuditAction.DELETED,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        changes={},
        ip_address=meta.get("ip"),
        user_agent=meta.get("user_agent", ""),
    )
