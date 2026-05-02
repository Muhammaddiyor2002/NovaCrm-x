from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "is_active",
            "is_staff",
            "mfa_enabled",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "is_active",
            "is_staff",
            "mfa_enabled",
            "is_email_verified",
            "date_joined",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    tenant_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "password", "tenant_name")
        read_only_fields = ("id",)

    def create(self, validated_data: dict) -> User:
        from apps.tenants.services import bootstrap_tenant_for_user

        tenant_name = validated_data.pop("tenant_name", "") or ""
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        bootstrap_tenant_for_user(
            user=user, tenant_name=tenant_name or f"{user.get_short_name()}'s Workspace"
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_current_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
