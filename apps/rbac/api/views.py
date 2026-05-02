from __future__ import annotations

from django.db.models import Q
from rest_framework import permissions, viewsets

from apps.rbac.models import Permission, Role
from apps.rbac.permissions import HasPermissionCode, IsTenantMember

from .serializers import PermissionSerializer, RoleSerializer


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, HasPermissionCode]
    required_permission = "members.manage"

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return Role.objects.filter(Q(tenant=tenant) | Q(tenant__isnull=True))

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, is_system=False)
