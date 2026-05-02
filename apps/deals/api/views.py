from __future__ import annotations

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.customers.api.views import TenantScopedModelViewSet
from apps.deals.models import Deal, DealStatus, Pipeline, Stage

from .serializers import DealSerializer, PipelineSerializer, StageSerializer


class PipelineViewSet(TenantScopedModelViewSet):
    queryset = Pipeline.objects.prefetch_related("stages").all()
    serializer_class = PipelineSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")

    @property
    def required_permission(self) -> str:
        return "deals.view" if self.action in {"list", "retrieve"} else "deals.update"


class StageViewSet(TenantScopedModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    filterset_fields = ("pipeline", "is_won", "is_lost")
    ordering_fields = ("position",)

    @property
    def required_permission(self) -> str:
        return "deals.view" if self.action in {"list", "retrieve"} else "deals.update"


class DealViewSet(TenantScopedModelViewSet):
    queryset = Deal.objects.select_related("stage", "company", "primary_contact", "owner").all()
    serializer_class = DealSerializer
    search_fields = ("title", "company__name", "primary_contact__last_name")
    ordering_fields = ("created_at", "amount", "expected_close_date", "probability")
    filterset_fields = ("pipeline", "stage", "status", "owner")

    @property
    def required_permission(self) -> str:
        return "deals.view" if self.action in {"list", "retrieve"} else "deals.update"

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        """Move a deal to a different stage (used by the Kanban UI)."""
        deal = self.get_object()
        stage_id = request.data.get("stage")
        if not stage_id:
            return Response({"detail": "stage is required"}, status=status.HTTP_400_BAD_REQUEST)
        stage = Stage.objects.filter(id=stage_id, pipeline_id=deal.pipeline_id).first()
        if stage is None:
            return Response({"detail": "Invalid stage."}, status=status.HTTP_400_BAD_REQUEST)
        deal.stage = stage
        deal.probability = stage.probability
        if stage.is_won:
            deal.status = DealStatus.WON
            deal.closed_at = timezone.now()
        elif stage.is_lost:
            deal.status = DealStatus.LOST
            deal.closed_at = timezone.now()
        else:
            deal.status = DealStatus.OPEN
            deal.closed_at = None
        deal.save()
        return Response(self.get_serializer(deal).data)
