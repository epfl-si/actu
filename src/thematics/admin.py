from django.contrib import admin

from .models import Thematic


@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    search_fields = Thematic.search_fields

    filter_horizontal = ("users",)

    list_display = (
        "label_en",
        "is_active",
        "is_main",
        "has_homepage",
        "order",
    )

    list_filter = (
        "is_active",
        "is_main",
        "has_homepage",
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "users":
            field.label_from_instance = lambda obj: (
                obj.email if obj.email else obj.username
            )
        return field
