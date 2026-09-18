from django import forms
from django.db import transaction
from django.forms.models import modelformset_factory
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from links.models import NewsLink
from translations.models import NewsTranslation

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


class NewsLinkForm(forms.ModelForm):
    class Meta:
        model = NewsLink
        fields = ["link"]
        widgets = {
            "link": forms.URLInput(attrs={"placeholder": "https://..."}),
        }


NewsLinkFormSet = modelformset_factory(
    NewsLink,
    form=NewsLinkForm,
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
        link_instance=None,
    ):
        self.news = NewsForm(post_data, instance=news_instance)
        self.translation = NewsTranslationForm(
            post_data, instance=translation_instance
        )
        self.language = language
        self.links = NewsLinkFormSet(
            post_data, queryset=link_instance, prefix="links"
        )

    def is_valid(self):
        news_valid = self.news.is_valid()
        translation_valid = self.translation.is_valid()
        links_valid = self.links.is_valid()
        return news_valid and translation_valid and links_valid

    def save(self, user):
        with transaction.atomic():
            news = self.news.save(user)
            self.translation.save(user, self.language, news)

            link_forms = self.links.save(commit=False)

            for link_form in link_forms:
                link_form.news = news
                link_form.language = self.language
                link_form.save()

            for deleted in self.links.deleted_objects:
                deleted.delete()

        return news.id
