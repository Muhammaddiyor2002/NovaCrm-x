"""AI-powered lead scoring."""

from __future__ import annotations

from apps.ai.providers import get_provider
from apps.leads.models import Lead


def score_with_ai(lead: Lead) -> int:
    provider = get_provider()
    text = (
        f"Lead: {lead.name}\n"
        f"Email: {lead.email}\n"
        f"Phone: {lead.phone}\n"
        f"Company: {lead.company_name}\n"
        f"Source: {lead.source}\n"
        f"Notes: {lead.notes or '(none)'}\n"
    )
    score = provider.score(
        text=text,
        criteria=(
            "Likelihood of converting into a paying customer based on signals like "
            "complete contact info, source quality, and intent indicators."
        ),
    )
    lead.score = score
    lead.save(update_fields=["score", "updated_at"])
    return score
