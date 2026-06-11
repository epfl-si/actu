from django.contrib import admin

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields = Entity.search_fields

    list_display = (
        "label_en",
        "slug",
        "is_active",
        "is_main",
        "has_homepage",
        "order",
    )

    list_filter = (
        "is_active",
        "is_main",
        "has_homepage",
    )
