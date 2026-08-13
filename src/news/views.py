from django import utils
from django.contrib import messages
from django.templatetags.i18n import language
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import News
from translations.models import NewsTranslation
from thematics.models import Thematic
from entities.models import Entity
from .forms import NewsForm
from .forms import NewsTranslationForm


User = get_user_model()

def _handle_post_action(request, language, news=None):
    news_form = NewsForm(request.POST, instance=news)
    translation_form = NewsTranslationForm(request.POST)
    if news_form.is_valid():
        news_saved = news_form.save(request)
        translation = NewsTranslation.get(news_saved.id, language)
        translation_form = NewsTranslationForm(request.POST, instance=translation)
        if translation_form.is_valid():
            translation_saved = translation_form.save(request, language, news_saved.id)
        else:
            return news_form, translation_form
        messages.success(
            request,
            _("The news %(title)s has been added successfully.")
            % {"title": translation_saved.title},
            )
        url_to_redirect = reverse(
            'edit_news',
            kwargs={
                'news_id': news_saved.id,
                "language": language
            })
        return HttpResponseRedirect(url_to_redirect)
    else:
        return news_form, translation_form

def _initialize_view(news=None):
    lang = utils.translation.get_language()

    selected_thematic_ids = set(news.thematics.values_list("id", flat=True)) if news else set()
    selected_entity_ids = set(news.entities.values_list("id", flat=True)) if news else set()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = thematic.get_label(lang)
        thematic.is_selected = thematic.id in selected_thematic_ids # TODO fix

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = entity.get_label(lang)
        entity.is_selected = entity.id in selected_entity_ids

    languages = [
        { 'code': 'en', 'label': 'English version', 'active': True },
        { 'code': 'fr', 'label': 'French version', 'active': False },
        { 'code': 'de', 'label': 'German version', 'active': False },
        { 'code': 'it', 'label': 'Italian version', 'active': False }
    ]

    return thematics, entities, languages

@login_required
def create_news(request, language):
    thematics, entities, languages = _initialize_view()

    if request.method == "POST":
        result = _handle_post_action(request, language)
        if isinstance(result, HttpResponseRedirect):
            return result

        news_form = NewsForm(request.POST)
        translation_form = NewsTranslationForm(request.POST)
    else:
        news_form = NewsForm() # TODO fix with parent form
        translation_form = NewsTranslationForm()

    context = {
        "news_form": news_form,
        "translation_form": translation_form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages
    }
    return render(request, "edit_news.html", context)

@login_required
def edit_news(request, news_id, language):
    news = get_object_or_404(News, id=news_id)
    thematics, entities, languages = _initialize_view(news)

    if request.method == "POST":
        response = _handle_post_action(request, news=news, language=language)
        if response:
            return response
        news_form = NewsForm(request.POST, instance=news)
        translation = get_object_or_404(NewsTranslation, news_id=news_id, language="en")
        translation_form = NewsTranslationForm(quest.POST, instance=translation)
    else:
        news_form = NewsForm(instance=news)
        translation = get_object_or_404(NewsTranslation, news_id=news_id, language="en")
        translation_form = NewsTranslationForm(instance=translation)

    context = {
        "news_form": news_form,
        "translation_form": translation_form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages
    }
    return render(request, "edit_news.html", context)

