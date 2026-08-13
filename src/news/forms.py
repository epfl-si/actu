from django import forms
from .models import News
from django.contrib import messages
from translations.models import NewsTranslation
from django.core.exceptions import ValidationError

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['thematics', 'entities']

    def clean(self):
        cleaned_data = super().clean()
        thematics = cleaned_data.get("thematics")
        entities = cleaned_data.get("entities")
        if not thematics:
            self.add_error("thematics", "No thematic provided.")
        if not entities:
            self.add_error("entities", "No entity provided.")
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
        fields = ['title']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        if not title or title == '':
            self.add_error("title", "No title provided.")
        return self.cleaned_data

    def save(self, request, language, news_id):
        is_new = self.instance.pk is None
        translation = super().save(commit=False)
        if is_new:
            translation.created_by = request.user
            translation.language = language
            translation.news_id = news_id
        translation.save()
        return translation

