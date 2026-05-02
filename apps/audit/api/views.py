from __future__ import annotations

from rest_framework import permissions, viewsets

from apps.audit.models import AuditLog
from apps.rbac.permissions import HasPermissionCode, IsTenantMember

from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, HasPermissionCode]
    required_permission = "tenant.manage"
    filterset_fields = ("action", "actor", "target_content_type")
    ordering_fields = ("created_at",)

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return AuditLog.all_tenants.none()
        return AuditLog.objects.filter(tenant=tenant).select_related("actor", "target_content_type")
