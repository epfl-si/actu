from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from utils.accred_client import AccredServiceClient

from .models import Homepage, HomepageTranslation

User = get_user_model()


def _handle_post_action(request, homepage):
    action = request.POST.get("action")

    if action == "add":
        sciper = request.POST.get("sciper")
        if not sciper:
            messages.error(request, _("No SCIPER provided."))
            return

        user = User.objects.filter(sciper=sciper).first()
        if not user:
            client = AccredServiceClient()
            person_details = client.get_person_details(sciper)

            if person_details:
                user, created = User.objects.get_or_create(
                    sciper=person_details["sciper"],
                    defaults={
                        "username": person_details["username"],
                        "first_name": person_details["first_name"],
                        "last_name": person_details["last_name"],
                        "email": person_details["email"],
                    },
                )
            else:
                messages.error(
                    request, _("Failed to add user, please try again.")
                )
                return

        if user:
            homepage.users.add(user)
            messages.success(
                request,
                _("The user %(first)s %(last)s has been added successfully.")
                % {"first": user.first_name, "last": user.last_name},
            )

    elif action == "remove":
        user_id = request.POST.get("user_id")
        if user_id:
            user = get_object_or_404(User, id=user_id)

            if homepage.users.filter(id=user.id).exists():
                homepage.users.remove(user)
                messages.success(
                    request,
                    _(
                        "The user %(first)s %(last)s has been removed "
                        "successfully."
                    )
                    % {"first": user.first_name, "last": user.last_name},
                )
            else:
                messages.warning(
                    request,
                    _(
                        "The user %(first)s %(last)s has no permission to this"
                        " homepage."
                    )
                    % {"first": user.first_name, "last": user.last_name},
                )


def _get_ajax_search_results(request, homepage):
    query = request.GET.get("q", "").strip()

    if len(query) < 3:
        return JsonResponse({"results": []})

    client = AccredServiceClient()
    external_results = client.search_persons_by_right(query)

    attached_scipers = {
        str(s) for s in homepage.users.values_list("sciper", flat=True)
    }
    data = []

    for user_data in external_results:
        sciper = user_data.get("sciper")
        display_name = user_data.get("display_name")

        if not sciper or not display_name:
            continue

        if str(sciper) not in attached_scipers:
            data.append(
                {
                    "sciper": sciper,
                    "text": display_name,
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                }
            )

    return JsonResponse({"results": data})


@login_required
def manage_homepage_users(request, pk):
    homepage = get_object_or_404(Homepage, pk=pk)

    is_attached = homepage.users.filter(id=request.user.id).exists()
    is_admin = request.user.is_superuser
    if not (is_attached or is_admin):
        raise PermissionDenied

    if request.method == "POST":
        _handle_post_action(request, homepage)
        return redirect("manage_homepage_users", pk=homepage.pk)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if is_ajax:
        return _get_ajax_search_results(request, homepage)

    context = {
        "homepage": homepage,
        "current_users": homepage.users.all().order_by(
            "last_name", "first_name"
        ),
    }
    return render(request, "manage_users.html", context)


def homepages(request):
    return render(request, "home.html", {})


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

    try:
        with transaction.atomic():
            HomepageTranslation.objects.create(
                homepage=homepage,
                language=lang,
                status=HomepageTranslation.Status.DRAFT,
                created_by=request.user,
            )
    except IntegrityError:
        messages.warning(
            request, _("A translation for this language already exists.")
        )
    else:
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
