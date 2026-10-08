from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models import NewsTranslation


@admin.register(NewsTranslation)
class NewsTranslationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "language",
        "status",
        "news_link",
        "slug",
        "created_at",
        "created_by",
        "published_at",
    ]

    search_fields = ["title"]

    list_filter = [
        "status",
        "language",
    ]

    autocomplete_fields = ["news"]

    list_select_related = ["news", "created_by"]

    readonly_fields = [
        "slug",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "published_at",
        "published_by",
    ]

    @admin.display(description=_("News"), ordering="news")
    def news_link(self, obj):
        url = reverse("admin:news_news_change", args=[obj.news_id])
        return format_html('<a href="{}">{}</a>', url, obj.news)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
