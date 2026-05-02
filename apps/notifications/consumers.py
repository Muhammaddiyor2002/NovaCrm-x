"""Per-user notifications WebSocket consumer."""

from __future__ import annotations

import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group_name = f"notifications.user.{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connected"})

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        # Echo for now — extended to ack/read in a future iteration.
        await self.send_json({"type": "ack", "payload": content})

    async def notify(self, event) -> None:
        """Broadcast handler invoked from the backend via channel_layer.group_send()."""
        await self.send(text_data=json.dumps(event["payload"]))
