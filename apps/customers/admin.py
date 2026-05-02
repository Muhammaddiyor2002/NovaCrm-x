from django.contrib import admin

from .models import Company, Contact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "industry", "size", "owner")
    list_filter = ("tenant", "size", "industry")
    search_fields = ("name", "website")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "tenant")
    list_filter = ("tenant",)
    search_fields = ("first_name", "last_name", "email")
