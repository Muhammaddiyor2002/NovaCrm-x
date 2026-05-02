from __future__ import annotations

import pytest

from apps.deals.models import Deal, DealStatus, Pipeline, Stage


@pytest.mark.django_db
def test_create_pipeline_and_move_deal(auth_client, tenant, user):
    pipeline = Pipeline.objects.create(tenant=tenant, name="Sales", is_default=True)
    s1 = Stage.objects.create(
        tenant=tenant, pipeline=pipeline, name="Discovery", position=0, probability=20
    )
    s2 = Stage.objects.create(
        tenant=tenant,
        pipeline=pipeline,
        name="Closed Won",
        position=1,
        probability=100,
        is_won=True,
    )
    deal = Deal.objects.create(
        tenant=tenant,
        pipeline=pipeline,
        stage=s1,
        title="Test deal",
        amount=1000,
        owner=user,
    )

    response = auth_client.post(
        f"/api/v1/deals/deals/{deal.id}/move/", {"stage": str(s2.id)}, format="json"
    )
    assert response.status_code == 200, response.content
    deal.refresh_from_db()
    assert deal.stage_id == s2.id
    assert deal.status == DealStatus.WON
    assert deal.closed_at is not None
