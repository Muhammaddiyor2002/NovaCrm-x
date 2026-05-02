from __future__ import annotations

from rest_framework import serializers

from apps.tenants.models import Membership, Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("id", "name", "slug", "status", "trial_ends_at", "created_at")
        read_only_fields = ("id", "slug", "status", "trial_ends_at", "created_at")


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "id",
            "user",
            "user_email",
            "tenant",
            "role",
            "role_name",
            "is_default",
            "joined_at",
        )
        read_only_fields = ("id", "user_email", "role_name", "joined_at")
