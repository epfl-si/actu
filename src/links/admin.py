from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("link", "news")

    list_filter = [
        "link",
    ]

    search_fields = ["link"]
