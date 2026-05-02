from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import MembershipViewSet, TenantViewSet

app_name = "tenants"

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("memberships", MembershipViewSet, basename="membership")

urlpatterns = router.urls
