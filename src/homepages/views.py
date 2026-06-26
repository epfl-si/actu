from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Homepage


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
