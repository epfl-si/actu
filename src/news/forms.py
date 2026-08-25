from django import forms
from django.forms.models import modelformset_factory
from tinymce.widgets import TinyMCE

from multi_ref.models import NewsMultiRef
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
        fields = ["title", "hat", "extract", "author", "funding", "references"]
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


class NewsLinkForm(forms.ModelForm):
    class Meta:
        model = NewsMultiRef
        fields = ["ref"]
        widgets = {
            "ref": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def save(self, news, language):
        link_forms = self.links.save(commit=False)

        for link_form in link_forms:
            link_form.news = news
            link_form.language = language
            link_form.type = NewsMultiRef.Type.LINK
            link_form.save()

        for deleted in self.links.deleted_objects:
            deleted.delete()


NewsLinkFormSet = modelformset_factory(
    NewsMultiRef,
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
        link_instance=None,
    ):
        self.news = NewsForm(post_data, instance=news_instance)
        self.translation = NewsTranslationForm(
            post_data, instance=translation_instance
        )
        self.links = NewsLinkFormSet(post_data, queryset=link_instance)
