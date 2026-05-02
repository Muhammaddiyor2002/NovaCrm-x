from __future__ import annotations

from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.notifications.models import Notification

from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Notification.all_tenants.none()
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if notif.read_at is None:
            notif.read_at = timezone.now()
            notif.save(update_fields=["read_at"])
        return Response(self.get_serializer(notif).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(read_at__isnull=True)
        qs.update(read_at=timezone.now())
        return Response({"count": qs.count()})
