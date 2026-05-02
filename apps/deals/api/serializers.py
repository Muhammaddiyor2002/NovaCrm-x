from __future__ import annotations

from rest_framework import serializers

from apps.deals.models import Deal, Pipeline, Stage


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("id", "pipeline", "name", "position", "probability", "is_won", "is_lost")
        read_only_fields = ("id",)


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = ("id", "name", "is_default", "description", "stages", "created_at")
        read_only_fields = ("id", "created_at")


class DealSerializer(serializers.ModelSerializer):
    weighted_amount = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)

    class Meta:
        model = Deal
        fields = (
            "id",
            "pipeline",
            "stage",
            "stage_name",
            "title",
            "company",
            "primary_contact",
            "owner",
            "amount",
            "currency",
            "probability",
            "weighted_amount",
            "expected_close_date",
            "closed_at",
            "status",
            "lost_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "weighted_amount", "stage_name", "created_at", "updated_at")
