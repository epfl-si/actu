from django.contrib import admin

from .models import Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = Language.search_fields

    list_display = ("code", "label_en", "label_fr", "label_de", "label_it")
