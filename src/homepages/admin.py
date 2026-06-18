from django.contrib import admin

from .models import Homepage


@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    filter_horizontal = ("users",)

    list_display = (
        "slug",
        "display_name",
        "thematic",
        "entity",
    )

    list_filter = (
        "thematic",
        "entity",
    )

    @admin.display(description="Name")
    def display_name(self, obj):
        if obj.thematic:
            return str(obj.thematic)
        if obj.entity:
            return str(obj.entity)
        return "-"
