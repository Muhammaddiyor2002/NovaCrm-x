from __future__ import annotations

from rest_framework import serializers

from apps.tickets.models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketReply
        fields = ("id", "ticket", "author", "body", "is_internal", "created_at")
        read_only_fields = ("id", "author", "created_at")


class TicketSerializer(serializers.ModelSerializer):
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "subject",
            "body",
            "contact",
            "assignee",
            "status",
            "priority",
            "sla_due_at",
            "resolved_at",
            "replies",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "resolved_at", "replies", "created_at", "updated_at")
