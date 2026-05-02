from __future__ import annotations

import pytest

from apps.leads.models import Lead, LeadSource, LeadStatus
from apps.leads.services import convert_lead, score_lead


@pytest.mark.django_db
def test_score_lead_heuristic(tenant, user):
    lead = Lead.objects.create(
        tenant=tenant,
        name="Lead One",
        email="lead1@example.com",
        phone="+1-555-0100",
        company_name="Prospect",
        source=LeadSource.REFERRAL,
        owner=user,
    )
    score = score_lead(lead)
    lead.refresh_from_db()
    assert score == lead.score
    assert score > 0


@pytest.mark.django_db
def test_convert_lead_creates_contact_and_deal(tenant, user):
    lead = Lead.objects.create(
        tenant=tenant,
        name="Lead Two",
        email="lead2@example.com",
        owner=user,
        source=LeadSource.WEBSITE,
    )
    contact, deal = convert_lead(lead, owner=user)
    assert contact.email == "lead2@example.com"
    assert deal.title.startswith("Deal for")
    lead.refresh_from_db()
    assert lead.status == LeadStatus.CONVERTED
