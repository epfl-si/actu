from django import forms
from django.db import transaction

from translations.models import NewsTranslation

from .models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["thematics", "entities", "format"]

    def clean(self):
        cleaned_data = super().clean()
        thematics = cleaned_data.get("thematics")
        format = cleaned_data.get("format")
        if not thematics:
            self.add_error("thematics", "No thematic provided.")
        if not format:
            self.add_error("format", "No format provided.")
        return self.cleaned_data

    def save(self, user):
        is_new = self.instance.pk is None
        news = super().save(commit=False)
        if is_new:
            news.created_by = user
        news.save()
        self.save_m2m()
        return news


class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
        fields = ["title"]

    def save(self, user, language, news_id):
        is_new = self.instance.pk is None
        translation = super().save(commit=False)
        if is_new:
            translation.created_by = user
            translation.language = language
            translation.news_id = news_id
        else:
            translation.updated_by = user
        translation.save()
        return translation


class NewsWithTranslationForm:
    def __init__(
        self,
        post_data=None,
        news_instance=None,
        translation_instance=None,
        language=None,
    ):
        self.news = NewsForm(post_data, instance=news_instance)
        self.translation = NewsTranslationForm(
            post_data, instance=translation_instance
        )
        self.language = language

    def is_valid(self):
        return self.news.is_valid() and self.translation.is_valid()

    def validate_and_save(self, user):
        if self.is_valid():
            with transaction.atomic():
                news = self.news.save(user)
                self.translation.save(
                    user, self.language, news.id
                )

            return news.id
