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
from .forms import NewsWithTranslationForm


User = get_user_model()

def _handle_post_action(request, language, news=None, translation=None):
    form = NewsWithTranslationForm(post_data=request.POST, news_instance=news, translation_instance=translation)
    if form.news.is_valid():
        news_saved = form.news.save(request)
        if form.translation.is_valid():
            translation_saved = form.translation.save(request, language, news_saved.id)
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

def _initialize_view(news=None):
    lang = utils.translation.get_language()

    selected_thematic_ids = set(news.thematics.values_list("id", flat=True)) if news else set()
    selected_entity_ids = set(news.entities.values_list("id", flat=True)) if news else set()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = thematic.get_label(lang)
        thematic.is_selected = thematic.id in selected_thematic_ids

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = entity.get_label(lang)
        entity.is_selected = entity.id in selected_entity_ids

    languages = [
        { 'code': 'en', 'label': 'English version' },
        { 'code': 'fr', 'label': 'French version' },
        { 'code': 'de', 'label': 'German version' },
        { 'code': 'it', 'label': 'Italian version' }
    ]

    return thematics, entities, languages

@login_required
def create_news(request, language):
    form = NewsWithTranslationForm()

    thematics, entities, languages = _initialize_view()

    if request.method == "POST":
        result = _handle_post_action(request, language)
        if isinstance(result, HttpResponseRedirect):
            return result

        form = NewsWithTranslationForm(request.POST)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages,
        "current_language": language,
        "current_path": 'create_news'
    }
    return render(request, "edit_news.html", context)

@login_required
def edit_news(request, news_id, language):
    news = get_object_or_404(News, id=news_id)
    translation = NewsTranslation.get(news_id, language)
    form = NewsWithTranslationForm(post_data=None, news_instance=news, translation_instance=translation)

    thematics, entities, languages = _initialize_view(news)

    if request.method == "POST":
        response = _handle_post_action(request, language, news, translation)
        if response:
            return response

        form = NewsWithTranslationForm(request.POST, news, translation)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages,
        "current_language": language,
        "current_path": 'edit_news'
    }
    return render(request, "edit_news.html", context)

