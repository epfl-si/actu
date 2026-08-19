from django import forms

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

    def save(self, request):
        is_new = self.instance.pk is None
        news = super().save(commit=False)
        if is_new:
            news.created_by = request.user
        news.save()
        self.save_m2m()
        return news


class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
        fields = ["title"]

    def save(self, request, language, news_id):
        is_new = self.instance.pk is None
        translation = super().save(commit=False)
        if is_new:
            translation.created_by = request.user
            translation.language = language
            translation.news_id = news_id
        else:
            translation.updated_by = request.user
        translation.save()
        return translation


class NewsWithTranslationForm:
    def __init__(
        self, post_data=None, news_instance=None, translation_instance=None
    ):
        self.news = NewsForm(post_data, instance=news_instance)
        self.translation = NewsTranslationForm(
            post_data, instance=translation_instance
        )
