from __future__ import annotations

from rest_framework import serializers

from apps.customers.models import Company, Contact


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "website",
            "industry",
            "size",
            "annual_revenue",
            "address",
            "owner",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = (
            "id",
            "company",
            "company_name",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "title",
            "owner",
            "tags",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "company_name", "full_name", "created_at", "updated_at")
