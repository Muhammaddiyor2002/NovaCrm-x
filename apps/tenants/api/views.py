from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tenants.middleware import resolve_tenant
from apps.tenants.models import Membership, Tenant

from .serializers import MembershipSerializer, TenantSerializer


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """Tenants the requesting user belongs to."""

    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        return Tenant.all_tenants.filter(memberships__user=user).distinct()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        tenant = (
            resolve_tenant(request) if getattr(request, "tenant", None) is None else request.tenant
        )
        if not tenant:
            return Response({"detail": "No active tenant."}, status=404)
        return Response(self.get_serializer(tenant).data)


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Membership.objects.none()
        return Membership.objects.filter(tenant=tenant).select_related("user", "role")
