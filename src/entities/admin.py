from django.contrib import admin

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        "label_en",
        "is_active",
        "is_main",
        "has_homepage",
        "order",
    )
