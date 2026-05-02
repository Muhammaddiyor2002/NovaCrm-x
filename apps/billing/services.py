"""Stripe integration helpers (graceful degrade when Stripe is not configured)."""

from __future__ import annotations

from typing import Any

from django.conf import settings


def stripe_enabled() -> bool:
    return bool(getattr(settings, "STRIPE_API_KEY", ""))


def get_client() -> Any:
    """Return a configured Stripe client, or None if disabled.

    We import lazily so the import doesn't crash environments without the
    `stripe` library installed (tests / local).
    """
    if not stripe_enabled():
        return None
    import stripe  # noqa: PLC0415

    stripe.api_key = settings.STRIPE_API_KEY
    return stripe


def create_checkout_session(*, tenant, plan, interval: str, success_url: str, cancel_url: str):
    """Create a Stripe Checkout session for the given tenant + plan."""
    stripe = get_client()
    if stripe is None:
        return {"url": f"{success_url}?demo=true", "id": "demo_session"}

    price_id = plan.stripe_price_id_yearly if interval == "yearly" else plan.stripe_price_id_monthly
    if not price_id:
        raise ValueError(f"Plan {plan.code} has no stripe price for interval {interval}")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(tenant.id),
        metadata={"tenant_id": str(tenant.id), "plan_code": plan.code},
    )
    return {"id": session.id, "url": session.url}
