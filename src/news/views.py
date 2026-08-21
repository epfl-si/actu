from django import utils
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from entities.models import Entity
from news_formats.models import NewsFormat
from thematics.models import Thematic
from translations.models import NewsTranslation

from .forms import NewsWithTranslationForm
from .models import News

User = get_user_model()


def _handle_post_action(request, language, news=None, translation=None):
    form = NewsWithTranslationForm(
        post_data=request.POST,
        news_instance=news,
        translation_instance=translation,
    )
    if form.news.is_valid():
        news_saved = form.news.save(request)
        if form.translation.is_valid():
            translation_saved = form.translation.save(
                request, language, news_saved.id
            )
            messages.success(
                request,
                _("The news %(title)s has been added successfully.")
                % {"title": translation_saved.title},
            )
            url_to_redirect = reverse(
                "edit_news",
                kwargs={"news_id": news_saved.id, "language": language},
            )
            return HttpResponseRedirect(url_to_redirect)


def _initialize_view():
    lang = utils.translation.get_language()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = thematic.get_label(lang)

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = entity.get_label(lang)

    formats = NewsFormat.objects.all()
    for format in formats:
        format.current_label = format.get_label(lang)

    languages = [
        {"code": "en", "label": _("English version")},
        {"code": "fr", "label": _("French version")},
        {"code": "de", "label": _("German version")},
        {"code": "it", "label": _("Italian version")},
    ]

    return thematics, entities, formats, languages


def _initialize_selected_values(request=None, news=None):
    if request is not None and request.method == "POST":
        # Re-rendering after a failed submission: reflect what the user picked
        selected_thematic_ids = set(
            map(int, request.POST.getlist("thematics"))
        )
        selected_entity_ids = set(map(int, request.POST.getlist("entities")))
        selected_format_id = int(request.POST.get("format"))
    elif news and news.pk:
        # Initial load of an existing News
        selected_thematic_ids = set(
            news.thematics.values_list("id", flat=True)
        )
        selected_entity_ids = set(news.entities.values_list("id", flat=True))
        selected_format_id = news.format_id
    else:
        # Initial load of a new News (create_news)
        selected_thematic_ids = set()
        selected_entity_ids = set()
        selected_format_id = None
    return selected_thematic_ids, selected_entity_ids, selected_format_id


@login_required
def create_news(request, language):
    thematics, entities, formats, languages = _initialize_view()

    form = NewsWithTranslationForm()
    selected_thematic_ids, selected_entity_ids, selected_format_id = (
        _initialize_selected_values(request)
    )

    if request.method == "POST":
        result = _handle_post_action(request, language)
        if result:
            return result

        form = NewsWithTranslationForm(request.POST)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "formats": formats,
        "languages": languages,
        "current_language": language,
        "selected_thematic_ids": selected_thematic_ids,
        "selected_entity_ids": selected_entity_ids,
        "selected_format_id": selected_format_id,
    }
    return render(request, "edit_news.html", context)


@login_required
def edit_news(request, news_id, language):
    thematics, entities, formats, languages = _initialize_view()

    news = get_object_or_404(News, id=news_id)
    translation = NewsTranslation.get(news_id, language)
    form = NewsWithTranslationForm(
        post_data=None, news_instance=news, translation_instance=translation
    )

    selected_thematic_ids, selected_entity_ids, selected_format_id = (
        _initialize_selected_values(request, news)
    )

    if request.method == "POST":
        result = _handle_post_action(request, language, news, translation)
        if result:
            return result

        form = NewsWithTranslationForm(request.POST, news, translation)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "formats": formats,
        "languages": languages,
        "current_language": language,
        "selected_thematic_ids": selected_thematic_ids,
        "selected_entity_ids": selected_entity_ids,
        "selected_format_id": selected_format_id,
    }
    return render(request, "edit_news.html", context)
