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

User = get_user_model()


@login_required
def create_news(request):
    news_var = "toto"
    context = {
        "news_var": news_var,
    }
    return render(request, "edit_news.html", context)

