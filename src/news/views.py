from django import utils
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from entities.models import Entity
from news_formats.models import NewsFormat
from thematics.models import Thematic
from translations.models import NewsTranslation
from utils.parser import _safe_int, _safe_int_set

from .forms import NewsWithTranslationForm
from .models import News


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

    if news_id:
        news_instance = get_object_or_404(News, id=news_id)
        translation_instance = news_instance.get_translation(language=lang)
    else:
        news_instance = None
        translation_instance = None

    form = NewsWithTranslationForm(
        post_data=request.POST or None,
        language=lang,
        news_instance=news_instance,
        translation_instance=translation_instance,
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
