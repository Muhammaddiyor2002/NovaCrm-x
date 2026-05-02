from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.usecases.email_writer import draft_email
from apps.ai.usecases.sentiment import analyze_sentiment
from apps.rbac.permissions import HasPermissionCode, IsTenantMember


class _AIPermissionMixin:
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, HasPermissionCode]
    required_permission = "ai.use"


class SentimentView(_AIPermissionMixin, APIView):
    def post(self, request) -> Response:
        text = request.data.get("text", "")
        if not text:
            return Response({"detail": "text is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"sentiment": analyze_sentiment(text)})


class EmailDraftView(_AIPermissionMixin, APIView):
    def post(self, request) -> Response:
        recipient = request.data.get("recipient_name", "there")
        context = request.data.get("context", "")
        tone = request.data.get("tone", "professional")
        if not context:
            return Response({"detail": "context is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"draft": draft_email(recipient_name=recipient, context=context, tone=tone)}
        )
