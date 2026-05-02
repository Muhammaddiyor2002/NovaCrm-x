from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import PermissionViewSet, RoleViewSet

app_name = "rbac"

router = DefaultRouter()
router.register("permissions", PermissionViewSet, basename="permission")
router.register("roles", RoleViewSet, basename="role")

urlpatterns = router.urls
