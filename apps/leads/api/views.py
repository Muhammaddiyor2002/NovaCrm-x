from __future__ import annotations

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.customers.api.views import TenantScopedModelViewSet
from apps.leads.models import Lead
from apps.leads.services import convert_lead, score_lead

from .serializers import LeadSerializer


class LeadViewSet(TenantScopedModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    search_fields = ("name", "email", "company_name", "phone")
    ordering_fields = ("created_at", "score", "status")
    filterset_fields = ("status", "source", "owner")
    permission_classes = TenantScopedModelViewSet.permission_classes + [permissions.IsAuthenticated]

    @property
    def required_permission(self) -> str:
        return "leads.view" if self.action in {"list", "retrieve"} else "leads.update"

    @action(detail=True, methods=["post"], url_path="score")
    def score(self, request, pk=None):
        lead = self.get_object()
        new_score = score_lead(lead)
        return Response({"id": str(lead.id), "score": new_score})

    @action(detail=True, methods=["post"], url_path="convert")
    def convert(self, request, pk=None):
        lead = self.get_object()
        contact, deal = convert_lead(lead, owner=request.user)
        return Response(
            {
                "lead_id": str(lead.id),
                "contact_id": str(contact.id),
                "deal_id": str(deal.id),
                "status": lead.status,
            }
        )
