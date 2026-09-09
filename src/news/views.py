from django import utils
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from entities.models import Entity
from news_formats.models import NewsFormat
from thematics.models import Thematic
from translations.models import NewsTranslation
from utils.parser import _safe_int, _safe_int_set

from .forms import NewsWithTranslationForm
from .models import News

User = get_user_model()


def list_news(request):
    current_lang = get_language()

    thematics = Thematic.objects.all()
    entities = Entity.objects.all()
    formats = NewsFormat.objects.all()

    search_query = request.GET.get("search", "").strip()
    selected_thematics = [int(i) for i in request.GET.getlist("thematics") if i.isdigit()]
    selected_entities = [int(i) for i in request.GET.getlist("entities") if i.isdigit()]
    selected_formats = [int(i) for i in request.GET.getlist("formats") if i.isdigit()]

    news_translations = (
        NewsTranslation.objects.filter(
            language=current_lang,
            status=NewsTranslation.Status.PUBLISHED,
            published_at__isnull=False,
        )
        .select_related(
            "news",
            "news__format",
        )
    )

    if search_query:
        news_translations = news_translations.filter(title__icontains=search_query)

    if selected_thematics:
        news_translations = news_translations.filter(news__thematics__in=selected_thematics)

    if selected_entities:
        news_translations = news_translations.filter(news__entities__in=selected_entities)

    if selected_formats:
        news_translations = news_translations.filter(news__format__in=selected_formats)

    if selected_thematics or selected_entities:
        news_translations = news_translations.distinct()

    news_translations = news_translations.order_by("-published_at")

    paginator = Paginator(news_translations, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1
    )

    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    context = {
        "news_translations": page_obj,
        "page_obj": page_obj,
        "page_range": page_range,
        "paginator": paginator,
        "query_string": query_dict.urlencode(),
        "thematics": thematics,
        "entities": entities,
        "formats": formats,
        "filters": {
            "search": search_query,
            "thematics": selected_thematics,
            "entities": selected_entities,
            "formats": selected_formats,
        },
    }

    return render(request, "list.html", context)


def _initialize_view():
    thematics = Thematic.objects.filter(is_active=True).order_by(
        f"label_{utils.translation.get_language()}"
    )
    entities = Entity.objects.filter(is_active=True).order_by(
        f"label_{utils.translation.get_language()}"
    )
    formats = NewsFormat.objects.all().order_by(
        f"label_{utils.translation.get_language()}"
    )
    languages = settings.LANGUAGES

    return thematics, entities, formats, languages


def _initialize_selected_values(request=None, news_form=None):
    if request is not None and request.method == "POST":
        # Re-rendering after a failed submission: reflect what the user picked
        selected_thematic_ids = _safe_int_set(
            request.POST.getlist("thematics")
        )
        selected_entity_ids = _safe_int_set(request.POST.getlist("entities"))
        selected_format_id = _safe_int(request.POST.get("format"))
    elif news_form and news_form.news.instance.pk:
        # Initial load of an existing News
        selected_thematic_ids = set(
            news_form.news.instance.thematics.values_list("id", flat=True)
        )
        selected_entity_ids = set(
            news_form.news.instance.entities.values_list("id", flat=True)
        )
        selected_format_id = news_form.news.instance.format_id
    else:
        # Initial load of a new News (create_news)
        selected_thematic_ids = set()
        selected_entity_ids = set()
        selected_format_id = None
    return selected_thematic_ids, selected_entity_ids, selected_format_id


def _initialize_form_and_render_view(request, lang, news_id=None):
    thematics, entities, formats, languages = _initialize_view()

    news = get_object_or_404(News, id=news_id) if news_id else None
    translation = news.get_translation(language=lang) if news else None

    form = NewsWithTranslationForm(
        post_data=request.POST or None,
        language=lang,
        news_instance=news,
        translation_instance=translation,
    )

    selected_thematic_ids, selected_entity_ids, selected_format_id = (
        _initialize_selected_values(request, form)
    )

    if request.method == "POST":
        if form.is_valid():
            news_id = form.save(request.user)
            messages.success(
                request, _("The news has been saved successfully.")
            )
            url_to_redirect = reverse(
                "edit_news",
                kwargs={"news_id": news_id, "lang": lang},
            )
            return HttpResponseRedirect(url_to_redirect)
        else:
            messages.error(
                request,
                _(
                    "The form contains errors. "
                    "Please correct the highlighted fields below."
                ),
            )

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "formats": formats,
        "languages": languages,
        "selected_thematic_ids": selected_thematic_ids,
        "selected_entity_ids": selected_entity_ids,
        "selected_format_id": selected_format_id,
    }
    return render(request, "edit_news.html", context)


@login_required
def create_news(request, lang):
    return _initialize_form_and_render_view(request, lang)


@login_required
def edit_news(request, news_id, lang):
    return _initialize_form_and_render_view(request, lang, news_id)


def _get_filters(request):
    entities = _safe_int_set(request.GET.getlist("entities"))
    statuses = {
        status
        for status in request.GET.getlist("status")
        if status in NewsTranslation.Status.values
    }

    if entities:
        active_entity_ids = set(
            Entity.objects.filter(is_active=True).values_list("id", flat=True)
        )
        if entities == active_entity_ids:
            entities = set()

    return {
        "search": request.GET.get("search", "").strip(),
        "status": statuses,
        "thematics": _safe_int_set(request.GET.getlist("thematics")),
        "entities": entities,
        "created_by": _safe_int_set(request.GET.getlist("created_by")),
        "formats": _safe_int_set(request.GET.getlist("formats")),
    }


def _apply_filters(news, filters):
    filter_search = filters.get("search")
    filter_statuses = filters.get("status")
    filter_thematics = filters.get("thematics")
    filter_entities = filters.get("entities")
    filter_created_by = filters.get("created_by")
    filter_formats = filters.get("formats")

    if filter_search:
        news = news.filter(translations__title__icontains=filter_search)

    if filter_statuses:
        news = news.filter(translations__status__in=filter_statuses)

    if filter_thematics:
        news = news.filter(
            thematics__id__in=filter_thematics,
        )

    if filter_entities:
        news = news.filter(
            entities__id__in=filter_entities,
        )

    if filter_created_by:
        news = news.filter(
            created_by_id__in=filter_created_by,
        )

    if filter_formats:
        news = news.filter(
            format_id__in=filter_formats,
        )

    return news.distinct()


@login_required
def manage_news(request):
    thematics, entities, formats, languages = _initialize_view()

    filters = _get_filters(request)

    translations_qs = NewsTranslation.objects.select_related(
        "created_by",
        "updated_by",
        "published_by",
    )

    news = News.objects.all().prefetch_related(
        Prefetch("translations", queryset=translations_qs)
    )

    news = _apply_filters(news, filters)

    paginator = Paginator(news, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1
    )

    languages = settings.LANGUAGES

    creators = (
        User.objects.filter(news_created__isnull=False)
        .distinct()
        .order_by("last_name", "first_name", "username")
    )

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
            "filters": filters,
            "statuses": NewsTranslation.Status,
            "thematics": thematics,
            "entities": entities,
            "creators": creators,
            "formats": formats,
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
