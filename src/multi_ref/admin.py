from django.contrib import admin

from .models import NewsMultiRef


@admin.register(NewsMultiRef)
class NewsMultiRefAdmin(admin.ModelAdmin):
    list_display = [
        "ref",
        "language",
        "type",
        "news",
    ]

    search_fields = ["ref"]

    list_filter = [
        "type",
        "language",
    ]

    autocomplete_fields = ["news"]
