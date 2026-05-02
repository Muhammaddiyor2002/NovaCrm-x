from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, PlanViewSet, SubscriptionViewSet, stripe_webhook

app_name = "billing"

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plan")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")
router.register("invoices", InvoiceViewSet, basename="invoice")

urlpatterns = router.urls + [
    path("webhook/stripe/", stripe_webhook, name="stripe-webhook"),
]
