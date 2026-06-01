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

    list_filter = (
        "is_active",
        "is_main",
        "has_homepage",
    )
