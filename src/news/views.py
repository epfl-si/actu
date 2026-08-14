from django import utils
from django.contrib import messages
from django.templatetags.i18n import language
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
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

def _initialize_view():
    lang = utils.translation.get_language()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = thematic.get_label(lang)

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = entity.get_label(lang)

    languages = [
        { 'code': 'en', 'label': _('English version') },
        { 'code': 'fr', 'label': _('French version') },
        { 'code': 'de', 'label': _('German version') },
        { 'code': 'it', 'label': _('Italian version') }
    ]

    return thematics, entities, languages

def _initialize_selected_values(request=None, news=None):
    if request is not None and request.method == "POST":
        # Re-rendering after a failed submission: reflect what the user picked
        selected_thematic_ids = set(map(int, request.POST.getlist("thematics")))
        selected_entity_ids = set(map(int, request.POST.getlist("entities")))
    elif news and news.pk:
        # Initial load of an existing News
        selected_thematic_ids = set(news.thematics.values_list("id", flat=True))
        selected_entity_ids = set(news.entities.values_list("id", flat=True))
    else:
        # Initial load of a new News (create_news)
        selected_thematic_ids = set()
        selected_entity_ids = set()
    return selected_thematic_ids, selected_entity_ids

@login_required
def create_news(request, language):
    thematics, entities, languages = _initialize_view()

    form = NewsWithTranslationForm()
    selected_thematic_ids, selected_entity_ids = _initialize_selected_values(request)

    if request.method == "POST":
        result = _handle_post_action(request, language)
        if result:
            return result

        form = NewsWithTranslationForm(request.POST)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages,
        "current_language": language,
        "selected_thematic_ids": selected_thematic_ids,
        "selected_entity_ids": selected_entity_ids,
        "current_path": 'create_news'
    }
    return render(request, "edit_news.html", context)

@login_required
def edit_news(request, news_id, language):
    thematics, entities, languages = _initialize_view()

    news = get_object_or_404(News, id=news_id)
    translation = NewsTranslation.get(news_id, language)
    form = NewsWithTranslationForm(post_data=None, news_instance=news, translation_instance=translation)

    selected_thematic_ids, selected_entity_ids = _initialize_selected_values(request, news)

    if request.method == "POST":
        result = _handle_post_action(request, language, news, translation)
        if result:
            return result

        form = NewsWithTranslationForm(request.POST, news, translation)

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages,
        "current_language": language,
        "selected_thematic_ids": selected_thematic_ids,
        "selected_entity_ids": selected_entity_ids,
        "current_path": 'edit_news'
    }
    return render(request, "edit_news.html", context)


@login_required
def manage_news(request):

    translations_qs = NewsTranslation.objects.select_related(
        "created_by",
        "updated_by",
        "published_by",
    )

    news = News.objects.all().prefetch_related(
        Prefetch("translations", queryset=translations_qs)
    )

    paginator = Paginator(news, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1
    )

    languages = settings.LANGUAGES

    news_rows = []
    for n in page_obj:
        translations_by_lang = {t.language: t for t in n.translations.all()}
        lang_cells = [
            (lang_code, lang_label, translations_by_lang.get(lang_code))
            for lang_code, lang_label in languages
        ]
        news_rows.append(
            {
                "news": n,
                "lang_cells": lang_cells,
            }
        )

    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    return render(
        request,
        "manage_news.html",
        {
            "news_rows": news_rows,
            "page_obj": page_obj,
            "page_range": page_range,
            "paginator": paginator,
            "query_string": query_dict.urlencode(),
        },
    )


@login_required
@require_POST
def delete_news_translation(request, news_id, lang):
    news_translation = get_object_or_404(
        NewsTranslation, news_id=news_id, language=lang
    )

    if news_translation.status == NewsTranslation.Status.ARCHIVED:
        messages.warning(request, _("This translation is already archived."))
        return redirect("manage_news")

    news_translation.status = NewsTranslation.Status.ARCHIVED
    news_translation.updated_by = request.user
    news_translation.save()

    messages.success(request, _("Translation archived successfully."))

    return redirect("manage_news")


@login_required
@require_POST
def restore_news_translation(request, news_id, lang):
    news_translation = get_object_or_404(
        NewsTranslation, news_id=news_id, language=lang
    )

    if news_translation.status != NewsTranslation.Status.ARCHIVED:
        messages.warning(request, _("This translation is not archived."))
        return redirect("manage_news")

    news_translation.status = NewsTranslation.Status.DRAFT
    news_translation.updated_by = request.user
    news_translation.save()

    messages.success(request, _("Translation restored successfully."))

    return redirect("manage_news")
