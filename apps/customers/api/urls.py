from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, ContactViewSet

app_name = "customers"

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="company")
router.register("contacts", ContactViewSet, basename="contact")

urlpatterns = router.urls
