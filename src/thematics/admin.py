from django.contrib import admin

from translations.admin import (
    TranslationInline,
)

from .models import Thematic


@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    list_display = ("label", "is_active", "is_main", "has_homepage", "order")
    inlines = [TranslationInline]
