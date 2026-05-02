from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "level", "verb", "message", "read_at", "created_at")
        read_only_fields = ("id", "level", "verb", "message", "created_at")
