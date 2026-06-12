from django.contrib import admin

from .models import NewsTranslation


@admin.register(NewsTranslation)
class NewsTranslationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "language",
        "status",
        "news",
        "created_at",
        "created_by",
        "published_at",
    ]

    search_fields = ["title"]

    list_filter = [
        "status",
        "language",
    ]

    autocomplete_fields = ["news", "language", "created_by"]

    readonly_fields = [
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "published_at",
        "published_by",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
