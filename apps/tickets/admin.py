from django.contrib import admin

from .models import Ticket, TicketReply


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "assignee", "tenant")
    list_filter = ("tenant", "status", "priority")
    search_fields = ("subject",)


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "is_internal", "created_at")
    list_filter = ("is_internal",)
