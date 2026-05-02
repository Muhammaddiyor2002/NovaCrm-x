from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_content_type", "tenant", "created_at")
    list_filter = ("action", "tenant", "target_content_type")
    search_fields = ("actor__email",)
    readonly_fields = (
        "actor",
        "action",
        "target_content_type",
        "target_object_id",
        "changes",
        "ip_address",
        "user_agent",
        "tenant",
        "created_at",
        "updated_at",
    )
