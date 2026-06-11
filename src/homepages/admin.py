from django.contrib import admin

from .models import Homepage


@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    filter_horizontal = ("users",)

    list_display = (
        "slug",
        "thematic",
        "entity",
    )

    list_filter = (
        "thematic",
        "entity",
    )
