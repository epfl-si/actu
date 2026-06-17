from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Thematic


@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    search_fields = Thematic.search_fields

    list_display = (
        "label_en",
        "is_active",
        "is_main",
        "has_homepage_link",
        "order",
    )

    list_filter = (
        "is_active",
        "is_main",
    )

    @admin.display(boolean=True, description=_("Has Homepage"))
    def has_homepage_link(self, obj):
        return hasattr(obj, "homepage")
