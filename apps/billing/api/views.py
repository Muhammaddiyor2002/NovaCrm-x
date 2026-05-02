from __future__ import annotations

import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.billing.models import Invoice, Plan, Subscription
from apps.billing.services import create_checkout_session
from apps.rbac.permissions import IsTenantMember

from .serializers import InvoiceSerializer, PlanSerializer, SubscriptionSerializer

log = logging.getLogger(__name__)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Subscription.all_tenants.none()
        return Subscription.objects.filter(tenant=tenant)

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        tenant = request.tenant
        plan_code = request.data.get("plan_code")
        interval = request.data.get("interval", "monthly")
        success_url = request.data.get(
            "success_url", request.build_absolute_uri("/billing/success/")
        )
        cancel_url = request.data.get("cancel_url", request.build_absolute_uri("/billing/cancel/"))
        plan = Plan.objects.filter(code=plan_code, is_active=True).first()
        if not plan:
            return Response({"detail": "Unknown plan."}, status=400)
        result = create_checkout_session(
            tenant=tenant,
            plan=plan,
            interval=interval,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return Response(result)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Invoice.all_tenants.none()
        return Invoice.objects.filter(tenant=tenant).order_by("-created_at")


@csrf_exempt
def stripe_webhook(request) -> HttpResponse:
    """Endpoint for Stripe webhook events. Verifies signature and updates state."""
    from apps.billing.services import get_client

    stripe = get_client()
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    secret = getattr(__import__("django").conf.settings, "STRIPE_WEBHOOK_SECRET", "")

    if stripe is None or not secret:
        log.warning("Stripe webhook called but Stripe is not configured.")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception:  # pragma: no cover
        return HttpResponse(status=400)

    event_type = event.get("type", "")
    data = event["data"]["object"]
    log.info("stripe.webhook", extra={"event": event_type})

    if event_type == "checkout.session.completed":
        tenant_id = data.get("metadata", {}).get("tenant_id")
        plan_code = data.get("metadata", {}).get("plan_code")
        if tenant_id and plan_code:
            plan = Plan.objects.filter(code=plan_code).first()
            if plan:
                Subscription.all_tenants.update_or_create(
                    tenant_id=tenant_id,
                    plan=plan,
                    defaults={
                        "status": "active",
                        "stripe_subscription_id": data.get("subscription", ""),
                    },
                )
    return HttpResponse(status=200)


# Decorate the function above so DRF doesn't complain when imported as a view.
stripe_webhook.csrf_exempt = True  # type: ignore[attr-defined]
