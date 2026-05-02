from __future__ import annotations

from rest_framework import serializers

from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    target_type = serializers.CharField(source="target_content_type.model", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_email",
            "action",
            "target_type",
            "target_object_id",
            "changes",
            "ip_address",
            "user_agent",
            "created_at",
        )
        read_only_fields = fields
