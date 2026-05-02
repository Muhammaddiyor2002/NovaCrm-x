"""Project URL configuration."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.views import healthz

api_v1_patterns = [
    path("auth/", include("apps.accounts.api.urls")),
    path("tenants/", include("apps.tenants.api.urls")),
    path("rbac/", include("apps.rbac.api.urls")),
    path("customers/", include("apps.customers.api.urls")),
    path("leads/", include("apps.leads.api.urls")),
    path("deals/", include("apps.deals.api.urls")),
    path("tasks/", include("apps.tasks.api.urls")),
    path("tickets/", include("apps.tickets.api.urls")),
    path("notifications/", include("apps.notifications.api.urls")),
    path("billing/", include("apps.billing.api.urls")),
    path("ai/", include("apps.ai.api.urls")),
    path("audit/", include("apps.audit.api.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="v1:schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="v1:schema"), name="redoc"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "v1"))),
    path("healthz", healthz, name="healthz"),
    path("metrics/", include("django_prometheus.urls")),
    path("", include("apps.dashboard.urls")),
]
