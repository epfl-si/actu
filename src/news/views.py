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


User = get_user_model()


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

    context = {
        "news_var": news_var,
        "thematics": thematics,
        "entities": entities
    }
    return render(request, "edit_news.html", context)

