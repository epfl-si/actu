from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.core.exceptions import ValidationError

from .models import Translation


class TranslationInlineFormSet(BaseGenericInlineFormSet):
    def clean(self):
        super().clean()
        languages_seen = set()

        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get("DELETE"):
                continue

            language = form.cleaned_data.get("language")
            if language:
                if language in languages_seen:
                    raise ValidationError(
                        f"Error : The language '{language}' is selected more \
                        than once for this element."
                    )
                languages_seen.add(language)


class TranslationInline(GenericTabularInline):
    model = Translation
    formset = TranslationInlineFormSet
    extra = 1
