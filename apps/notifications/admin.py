from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "verb", "level", "read_at", "tenant", "created_at")
    list_filter = ("level", "tenant")
    search_fields = ("verb", "message")
