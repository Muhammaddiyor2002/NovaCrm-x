from __future__ import annotations

from rest_framework import serializers

from apps.leads.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "company_name",
            "source",
            "status",
            "score",
            "owner",
            "notes",
            "converted_contact",
            "converted_deal",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "score",
            "converted_contact",
            "converted_deal",
            "created_at",
            "updated_at",
        )
