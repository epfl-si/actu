from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Translation, Thematic


class TranslationInline(GenericTabularInline):
    model = Translation
    extra = 1  # number of empty forms shown by default

@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    inlines = [TranslationInline]
