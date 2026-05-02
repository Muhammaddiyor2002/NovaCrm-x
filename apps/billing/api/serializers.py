from __future__ import annotations

from rest_framework import serializers

from apps.billing.models import Invoice, Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "code",
            "name",
            "description",
            "price_monthly",
            "price_yearly",
            "max_users",
            "max_contacts",
            "features",
            "is_active",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan",
            "plan_name",
            "interval",
            "status",
            "started_at",
            "current_period_end",
            "cancel_at_period_end",
        )
        read_only_fields = (
            "id",
            "plan_name",
            "status",
            "started_at",
            "current_period_end",
            "cancel_at_period_end",
        )


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = (
            "id",
            "subscription",
            "number",
            "amount",
            "currency",
            "status",
            "issued_at",
            "due_at",
            "paid_at",
            "pdf_url",
            "created_at",
        )
        read_only_fields = fields
