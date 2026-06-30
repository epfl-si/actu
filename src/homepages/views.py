from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .models import Homepage, HomepageTranslation


def homepages(request):

    return render(
        request,
        "home.html",
        {},
    )


@login_required
def manage_homepages(request):

    homepages = (
        Homepage.objects.filter(users=request.user)
        .prefetch_related(
            "translations",
            "translations__created_by",
            "translations__published_by",
        )
        .select_related("thematic", "entity")
    )

    languages = settings.LANGUAGES

    homepage_rows = []
    for homepage in homepages:
        translations_by_lang = {
            t.language: t for t in homepage.translations.all()
        }
        lang_cells = [
            (lang_code, lang_label, translations_by_lang.get(lang_code))
            for lang_code, lang_label in languages
        ]
        homepage_rows.append(
            {
                "homepage": homepage,
                "lang_cells": lang_cells,
            }
        )

    return render(
        request,
        "manage_homepages.html",
        {
            "homepage_rows": homepage_rows,
            "languages": languages,
        },
    )


@login_required
def create_homepage_translation(request, homepage_id, lang):
    homepage = get_object_or_404(
        Homepage.objects.filter(users=request.user),
        pk=homepage_id,
    )

    valid_lang_codes = [code for code, _ in settings.LANGUAGES]
    if lang not in valid_lang_codes:
        messages.error(request, _("Invalid language."))
        return redirect("manage_homepages")

    if HomepageTranslation.objects.filter(
        homepage=homepage, language=lang
    ).exists():
        messages.warning(
            request, _("A translation for this language already exists.")
        )
        return redirect("manage_homepages")

    HomepageTranslation.objects.create(
        homepage=homepage,
        language=lang,
        status=HomepageTranslation.Status.DRAFT,
        created_by=request.user,
    )

    messages.success(request, _("Translation created successfully."))

    return redirect("manage_homepages")
