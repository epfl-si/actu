from django.contrib import admin

from translations.admin import (
    TranslationInline,
)

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("label", "is_active", "is_main", "has_homepage")
    inlines = [TranslationInline]
