from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "due_at", "assignee", "tenant")
    list_filter = ("tenant", "status", "priority")
    search_fields = ("title",)
