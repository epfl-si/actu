from django.contrib import admin
from django.db import models

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["thematic", "entity"]:
            object_id = request.resolver_match.kwargs.get('object_id')

            if object_id:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    models.Q(homepage__isnull=True) | models.Q(homepage__id=object_id)
                )
            else:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    homepage__isnull=True
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
