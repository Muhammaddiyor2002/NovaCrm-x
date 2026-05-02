from __future__ import annotations

from rest_framework import serializers

from apps.rbac.models import Permission, Role


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "code", "description")


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        slug_field="code", many=True, queryset=Permission.objects.all(), required=False
    )

    class Meta:
        model = Role
        fields = ("id", "name", "slug", "is_system", "description", "permissions")
        read_only_fields = ("id", "slug", "is_system")
