from django import utils
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

from .models import News
from translations.models import NewsTranslation
from thematics.models import Thematic
from entities.models import Entity
from .forms import NewsForm


User = get_user_model()

def _handle_post_action(request):
    action = request.POST.get("action")

    if action == "add":
        thematic = request.POST.getlist("thematics")
        if not thematic:
            messages.error(request, _("No thematic provided."))
            return
        entity = request.POST.getlist("entities")
        if not entity:
            messages.error(request, _("No entity provided."))
            return

        print(entity)
        news_form = NewsForm(request.POST)

        if news_form.is_valid():
            news = news_form.save(commit=False)
            news.created_by = request.user
            news.save()
            news_form.save_m2m()
            messages.success(
                request,
                _("The news %(title) has been added successfully.")
                % {"title": "test"},
                )
            return True
        else:
            logger.error("error saving")
            return False


@login_required
def create_news(request):
    news_var = "it"
    lang = utils.translation.get_language()

    thematics = Thematic.objects.all()
    for thematic in thematics:
        thematic.current_label = getattr(thematic, f"label_{lang}")

    entities = Entity.objects.all()
    for entity in entities:
        entity.current_label = getattr(entity, f"label_{lang}")

    languages = [
        { 'code': 'en', 'label': 'English version', 'active': True },
        { 'code': 'fr', 'label': 'French version', 'active': False },
        { 'code': 'de', 'label': 'German version', 'active': False },
        { 'code': 'it', 'label': 'Italian version', 'active': False }
    ]

    if request.method == "POST":
        created = _handle_post_action(request)
        if created:
            return redirect("create_news")
    else:
        form = NewsForm()

    context = {
        "news_var": news_var,
        "thematics": thematics,
        "entities": entities,
        "languages": languages
    }
    return render(request, "edit_news.html", context)

