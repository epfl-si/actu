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

def _handle_post_action(request, news=None):
    thematic = request.POST.getlist("thematics")
    if not thematic:
        messages.error(request, _("No thematic provided."))
        return
    entity = request.POST.getlist("entities")
    if not entity:
        messages.error(request, _("No entity provided."))
        return

    news_form = NewsForm(request.POST, instance=news)

    if news_form.is_valid():
        is_new = news_form.instance.pk is None

        news_saved = news_form.save(commit=False)
        if is_new:
            news_saved.created_by = request.user
        news_saved.save()
        news_form.save_m2m()

        print("rosajlsdkf")
        print(news_saved.id)
        print("end rosa")
        try:
            translation_from_db = NewsTranslation.objects.get(
                news_id=news_saved.id,
                language=request.POST.get("language")
            )
        except NewsTranslation.DoesNotExist:
            translation_from_db = None
        print("rosa 8734682346837")
        translation_form = NewsTranslationForm(request.POST, instance=translation_from_db)
        if translation_form.is_valid():
            is_new_translation = translation_form.instance.pk is None
            translation = translation_form.save(commit=False)
            if is_new_translation:
                translation.created_by = request.user
            translation.news_id = news_saved.id
            translation.save()
        messages.success(
            request,
            _("The news %(title)s has been added successfully.")
            % {"title": translation.title},
            )
        url_to_redirect = reverse(
            'edit_news',
            kwargs={
                'news_id': news_saved.id
            })
        return HttpResponseRedirect(url_to_redirect)
    else:
        print(news_form.errors.as_data())
        print(translation_form.errors.as_data())

def _initialize_view(news=None):
    lang = utils.translation.get_language()

    selected_thematic_ids = set(news.thematics.values_list("id", flat=True)) if news else set()
    selected_entity_ids = set(news.entities.values_list("id", flat=True)) if news else set()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = getattr(thematic, f"label_{lang}")
        thematic.is_selected = thematic.id in selected_thematic_ids

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = getattr(entity, f"label_{lang}")
        entity.is_selected = entity.id in selected_entity_ids

    languages = [
        { 'code': 'en', 'label': 'English version', 'active': True },
        { 'code': 'fr', 'label': 'French version', 'active': False },
        { 'code': 'de', 'label': 'German version', 'active': False },
        { 'code': 'it', 'label': 'Italian version', 'active': False }
    ]

    return thematics, entities, languages


@login_required
def create_news(request):
    thematics, entities, languages = _initialize_view()

    if request.method == "POST":
        return _handle_post_action(request)
    else:
        form = NewsForm()

    context = {
        "form": form,
        "thematics": thematics,
        "entities": entities,
        "languages": languages
    }
    return render(request, "edit_news.html", context)

@login_required
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    thematics, entities, languages = _initialize_view(news)

    if request.method == "POST":
        response = _handle_post_action(request, news=news)
        if response:
            return response
        news_form = NewsForm(request.POST, instance=news)
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

    languages = settings.LANGUAGES

    news_rows = []
    for n in news:
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

    return render(
        request,
        "manage_news.html",
        {
            "news_rows": news_rows,
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
