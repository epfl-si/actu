from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Translation, Entity


class TranslationInline(GenericTabularInline):
    model = Translation
    extra = 1  # number of empty forms shown by default

@admin.register(Entity)
class ThematicAdmin(admin.ModelAdmin):
    inlines = [TranslationInline]
