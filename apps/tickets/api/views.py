from __future__ import annotations

from django.utils import timezone

from apps.customers.api.views import TenantScopedModelViewSet
from apps.tickets.models import Ticket, TicketReply, TicketStatus

from .serializers import TicketReplySerializer, TicketSerializer


class TicketViewSet(TenantScopedModelViewSet):
    queryset = Ticket.objects.prefetch_related("replies").all()
    serializer_class = TicketSerializer
    search_fields = ("subject", "body")
    ordering_fields = ("created_at", "priority", "status")
    filterset_fields = ("status", "priority", "assignee", "contact")

    @property
    def required_permission(self) -> str:
        return "tickets.view" if self.action in {"list", "retrieve"} else "tickets.update"

    def perform_update(self, serializer):
        instance: Ticket = serializer.save()
        if (
            instance.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}
            and not instance.resolved_at
        ):
            instance.resolved_at = timezone.now()
            instance.save(update_fields=["resolved_at"])
        elif (
            instance.status not in {TicketStatus.RESOLVED, TicketStatus.CLOSED}
            and instance.resolved_at
        ):
            instance.resolved_at = None
            instance.save(update_fields=["resolved_at"])


class TicketReplyViewSet(TenantScopedModelViewSet):
    queryset = TicketReply.objects.all()
    serializer_class = TicketReplySerializer
    filterset_fields = ("ticket", "is_internal")

    @property
    def required_permission(self) -> str:
        return "tickets.view" if self.action in {"list", "retrieve"} else "tickets.update"

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, author=self.request.user)
