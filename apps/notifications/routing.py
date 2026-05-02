"""Channels websocket routing for realtime notifications."""

from __future__ import annotations

from django.urls import path

from .consumers import NotificationsConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationsConsumer.as_asgi()),
]
