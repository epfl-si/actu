from django.contrib import admin

from ..models.url import NewsUrl


@admin.register(NewsUrl)
class NewsUrlAdmin(admin.ModelAdmin):
    list_display = [
        "url",
        "translation",
    ]

    search_fields = ["url"]
