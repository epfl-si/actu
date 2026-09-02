from django.contrib import admin

from .models import GlobalAuditLog


@admin.register(GlobalAuditLog)
class GlobalAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "content_type",
        "object_id",
        "user",
        "action",
    )
    list_filter = ("content_type", "action", "created_at")
    search_fields = ("details", "object_id")
    readonly_fields = [f.name for f in GlobalAuditLog._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
