from django.contrib import admin

from .models import NewsLink


@admin.register(NewsLink)
class NewsLinkAdmin(admin.ModelAdmin):
    list_display = [
        "link",
        "language",
        "news",
    ]

    search_fields = ["link"]

    list_filter = [
        "language",
    ]

    autocomplete_fields = ["news"]
