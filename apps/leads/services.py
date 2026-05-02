"""Lead business logic: scoring, routing, conversion."""

from __future__ import annotations

from django.db import transaction

from apps.customers.models import Contact
from apps.deals.models import Deal, Pipeline, Stage

from .models import Lead, LeadStatus


def score_lead(lead: Lead) -> int:
    """Compute and persist a 0–100 score for the lead.

    This is a deterministic heuristic used as a fallback when the AI provider
    is `dummy` or unconfigured. Override / call into AI in production via
    `apps.ai.usecases.lead_scoring`.
    """
    score = 0
    if lead.email:
        score += 25
    if lead.phone:
        score += 15
    if lead.company_name:
        score += 20
    if lead.source in {"referral", "event"}:
        score += 25
    elif lead.source in {"website", "ad"}:
        score += 15
    score = min(100, score)
    lead.score = score
    lead.save(update_fields=["score", "updated_at"])
    return score


@transaction.atomic
def convert_lead(lead: Lead, *, owner) -> tuple[Contact, Deal]:
    """Convert a lead into a Contact + initial open Deal."""
    if lead.status == LeadStatus.CONVERTED and lead.converted_contact and lead.converted_deal:
        return lead.converted_contact, lead.converted_deal

    parts = lead.name.split(" ", 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""

    contact = Contact.objects.create(
        tenant=lead.tenant,
        first_name=first,
        last_name=last,
        email=lead.email,
        phone=lead.phone,
        owner=owner,
    )

    pipeline = Pipeline.objects.filter(tenant=lead.tenant, is_default=True).first()
    if pipeline is None:
        pipeline = Pipeline.objects.create(tenant=lead.tenant, name="Sales", is_default=True)
        Stage.objects.bulk_create(
            [
                Stage(tenant=lead.tenant, pipeline=pipeline, name=n, position=i, probability=p)
                for i, (n, p) in enumerate(
                    [
                        ("Qualification", 10),
                        ("Discovery", 25),
                        ("Proposal", 50),
                        ("Negotiation", 75),
                        ("Closed Won", 100),
                        ("Closed Lost", 0),
                    ]
                )
            ]
        )
    first_stage = pipeline.stages.order_by("position").first()
    deal = Deal.objects.create(
        tenant=lead.tenant,
        pipeline=pipeline,
        stage=first_stage,
        title=f"Deal for {lead.name}",
        primary_contact=contact,
        owner=owner,
        amount=0,
    )

    lead.converted_contact = contact
    lead.converted_deal = deal
    lead.status = LeadStatus.CONVERTED
    lead.save(update_fields=["converted_contact", "converted_deal", "status", "updated_at"])
    return contact, deal
