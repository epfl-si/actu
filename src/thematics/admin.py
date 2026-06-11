from django.contrib import admin

from .models import Thematic


@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    search_fields = Thematic.search_fields

    list_display = (
        "label_en",
        "is_active",
        "is_main",
        "has_homepage",
        "order",
    )

    ordering = ("-is_active", "-is_main", "order", "label_en")

    list_filter = (
        "is_active",
        "is_main",
        "has_homepage",
    )

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        Thematic.reorder_everything()
