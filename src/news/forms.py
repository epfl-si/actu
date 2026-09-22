from django import forms
from django.db import transaction
from django.forms.models import modelformset_factory
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from translations.models import NewsTranslation
from urls.models import NewsUrl

from .models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["thematics", "entities", "format"]
        error_messages = {
            "thematics": {
                "required": _("A news must have at least one thematic."),
            },
        }

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
        fields = [
            "title",
            "standfirst",
            "extract",
            "author",
            "funding",
            "references",
        ]
        widgets = {
            "author": TinyMCE(mce_attrs={"height": 130}),
            "extract": TinyMCE(
                mce_attrs={
                    "height": 250,
                    "menubar": False,
                    "plugins": "lists link anchor code",
                    "toolbar": "bold italic underline | bullist numlist indent"
                    " outdent  | subscript superscript | blocks | link anchor"
                    " | undo redo | fullscreen | code",
                }
            ),
        }

    def save(self, user, language, news):
        is_new = self.instance.pk is None
        translation = super().save(commit=False)
        if is_new:
            translation.created_by = user
            translation.language = language
            translation.news = news
        else:
            translation.updated_by = user
        translation.save()
        return translation


class NewsUrlForm(forms.ModelForm):
    class Meta:
        model = NewsUrl
        fields = ["url"]
        widgets = {
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }


NewsUrlFormSet = modelformset_factory(
    NewsUrl,
    form=NewsUrlForm,
    extra=1,
    can_delete=True,
)


class NewsWithTranslationForm:
    def __init__(
        self,
        post_data=None,
        news_instance=None,
        translation_instance=None,
        language=None,
        urls_queryset=None,
    ):
        self.news = NewsForm(post_data, instance=news_instance)
        self.translation = NewsTranslationForm(
            post_data, instance=translation_instance
        )
        self.language = language
        self.urls = NewsUrlFormSet(
            post_data, queryset=urls_queryset, prefix="urls"
        )

    def is_valid(self):
        news_valid = self.news.is_valid()
        translation_valid = self.translation.is_valid()
        urls_valid = self.urls.is_valid()
        return news_valid and translation_valid and urls_valid

    def save(self, user):
        with transaction.atomic():
            news = self.news.save(user)
            self.translation.save(user, self.language, news)

            url_forms = self.urls.save(commit=False)

            for url_form in url_forms:
                url_form.translation = self.translation.instance
                url_form.save()

            for deleted in self.urls.deleted_objects:
                deleted.delete()

        return news.id
