from django import forms
from .models import News
from translations.models import NewsTranslation

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['thematics', 'entities']

class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
        fields = ['title', 'language']
