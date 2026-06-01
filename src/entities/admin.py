from django.contrib import admin

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields = [
        "label_en",
        "label_fr",
        "label_de",
        "label_it",
    ]
    list_display = (
        "label_en",
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
