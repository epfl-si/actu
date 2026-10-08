from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "format",
        "translation_statuses",
        "created_at",
        "created_by",
        "is_under_cc_license",
    ]
    search_fields = ["translations__title"]
    list_select_related = ["format", "created_by"]
    readonly_fields = ["created_by", "translations_overview"]

    @admin.display(description=_("Translations"))
    def translation_statuses(self, obj):
        statuses = {
            translation.language: translation.get_status_display()
            for translation in obj.translations.all()
        }
        return format_html_join(
            " · ",
            "{}: {}",
            (
                (code, statuses.get(code, "—"))
                for code, _ in settings.LANGUAGES
            ),
        )

    @admin.display(description=_("Translations"))
    def translations_overview(self, obj):
        translations = sorted(obj.translations.all(), key=lambda t: t.language)
        return format_html_join(
            mark_safe("<br>"),
            '<a href="{}">{} — {}</a>',
            (
                (
                    reverse(
                        "admin:translations_newstranslation_change",
                        args=[translation.pk],
                    ),
                    translation,
                    translation.get_status_display(),
                )
                for translation in translations
            ),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("translations")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
