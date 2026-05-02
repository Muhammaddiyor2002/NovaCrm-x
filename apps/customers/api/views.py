from __future__ import annotations

from rest_framework import permissions, viewsets

from apps.customers.models import Company, Contact
from apps.rbac.permissions import HasPermissionCode, IsObjectInTenant, IsTenantMember

from .serializers import CompanySerializer, ContactSerializer


class TenantScopedModelViewSet(viewsets.ModelViewSet):
    """Base viewset that auto-stamps the active tenant on create."""

    permission_classes = [
        permissions.IsAuthenticated,
        IsTenantMember,
        HasPermissionCode,
        IsObjectInTenant,
    ]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class CompanyViewSet(TenantScopedModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ("name", "website", "industry")
    ordering_fields = ("name", "created_at", "annual_revenue")
    filterset_fields = ("size", "industry", "owner")

    @property
    def required_permission(self) -> str:
        return "customers.view" if self.action in {"list", "retrieve"} else "customers.update"


class ContactViewSet(TenantScopedModelViewSet):
    queryset = Contact.objects.select_related("company").all()
    serializer_class = ContactSerializer
    search_fields = ("first_name", "last_name", "email", "phone")
    ordering_fields = ("last_name", "created_at")
    filterset_fields = ("company", "owner")

    @property
    def required_permission(self) -> str:
        return "customers.view" if self.action in {"list", "retrieve"} else "customers.update"
