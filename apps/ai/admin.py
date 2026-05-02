from django.contrib import admin

from .models import AIInvocation


@admin.register(AIInvocation)
class AIInvocationAdmin(admin.ModelAdmin):
    list_display = ("use_case", "provider", "model", "success", "tenant", "created_at")
    list_filter = ("use_case", "provider", "success")
