from django.contrib import admin

from .models import Permission, Role


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "description")
    search_fields = ("code",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "tenant", "is_system")
    list_filter = ("is_system", "tenant")
    search_fields = ("name", "slug")
    filter_horizontal = ("permissions",)
