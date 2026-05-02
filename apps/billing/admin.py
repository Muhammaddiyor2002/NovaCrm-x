from django.contrib import admin

from .models import Invoice, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "price_monthly", "price_yearly", "is_active")
    search_fields = ("code", "name")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "status", "interval", "current_period_end")
    list_filter = ("status", "interval")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("tenant", "number", "amount", "currency", "status", "paid_at")
    list_filter = ("status", "currency")
