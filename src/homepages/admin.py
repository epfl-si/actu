from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("thematic", "entity")

    @admin.display(description=_("Name"))
    def display_name(self, obj):
        return obj.display_name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["thematic", "entity"]:
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    models.Q(homepage__isnull=True)
                    | models.Q(homepage__id=object_id)
                )
            else:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    homepage__isnull=True
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
