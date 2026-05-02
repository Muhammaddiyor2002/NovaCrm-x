from django.contrib import admin

from .models import Membership, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "status", "trial_ends_at")
    search_fields = ("name", "slug", "owner__email")
    list_filter = ("status",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "is_default", "joined_at")
    list_filter = ("tenant", "role")
    search_fields = ("user__email", "tenant__name")
