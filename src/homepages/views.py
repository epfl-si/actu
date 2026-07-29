from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import Homepage, HomepageTranslation


def homepages(request):

    return render(
        request,
        "home.html",
        {},
    )


@login_required
def manage_homepages(request):

    translations_qs = HomepageTranslation.objects.select_related(
        "created_by",
        "updated_by",
        "published_by",
    )

    homepages = (
        Homepage.objects.filter(users=request.user)
        .select_related("thematic", "entity")
        .prefetch_related(Prefetch("translations", queryset=translations_qs))
        .order_by("thematic__order", "entity__order")
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
@require_POST
def create_homepage_translation(request, homepage_id, lang):
    homepage = get_object_or_404(
        Homepage.objects.filter(users=request.user),
        pk=homepage_id,
    )

    valid_lang_codes = [code for code, _ in settings.LANGUAGES]
    if lang not in valid_lang_codes:
        raise Http404

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


@login_required
@require_POST
def delete_homepage_translation(request, homepage_id, lang):
    homepage = get_object_or_404(
        Homepage.objects.filter(users=request.user),
        pk=homepage_id,
    )

    translation = get_object_or_404(
        HomepageTranslation,
        homepage=homepage,
        language=lang,
    )

    if translation.status == HomepageTranslation.Status.ARCHIVED:
        messages.warning(request, _("This translation is already archived."))
        return redirect("manage_homepages")

    translation.status = HomepageTranslation.Status.ARCHIVED
    translation.updated_by = request.user
    translation.save()

    messages.success(request, _("Translation archived successfully."))

    return redirect("manage_homepages")


@login_required
@require_POST
def restore_homepage_translation(request, homepage_id, lang):
    homepage = get_object_or_404(
        Homepage.objects.filter(users=request.user),
        pk=homepage_id,
    )

    translation = get_object_or_404(
        HomepageTranslation,
        homepage=homepage,
        language=lang,
    )

    if translation.status != HomepageTranslation.Status.ARCHIVED:
        messages.warning(request, _("This translation is not archived."))
        return redirect("manage_homepages")

    translation.status = HomepageTranslation.Status.DRAFT
    translation.updated_by = request.user
    translation.save()

    messages.success(request, _("Translation restored successfully."))

    return redirect("manage_homepages")
