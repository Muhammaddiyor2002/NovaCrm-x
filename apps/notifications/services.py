"""Helper to enqueue notifications and broadcast over WebSocket."""

from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def push_notification(
    *, tenant, recipient, verb: str, message: str, level: str = "info"
) -> Notification:
    notif = Notification.objects.create(
        tenant=tenant, recipient=recipient, verb=verb, message=message, level=level
    )
    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(
            f"notifications.user.{recipient.id}",
            {
                "type": "notify",
                "payload": {
                    "id": str(notif.id),
                    "verb": verb,
                    "message": message,
                    "level": level,
                },
            },
        )
    return notif
