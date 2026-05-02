from django.contrib import admin

from .models import Deal, Pipeline, Stage


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "is_default")
    list_filter = ("tenant", "is_default")


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name", "pipeline", "position", "probability", "is_won", "is_lost")
    list_filter = ("pipeline",)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("title", "stage", "amount", "currency", "status", "owner", "tenant")
    list_filter = ("tenant", "status", "stage")
    search_fields = ("title",)
