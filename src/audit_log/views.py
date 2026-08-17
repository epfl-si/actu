import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext as _

from .models import GlobalAuditLog

User = get_user_model()


def _apply_filters(logs, request):
    filter_type = request.GET.get("type", "")
    filter_user = request.GET.get("user", "")
    filter_action = request.GET.get("action", "")
    filter_search = request.GET.get("search", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if filter_type:
        logs = logs.filter(content_type__model=filter_type)
    if filter_user:
        logs = logs.filter(user__id=filter_user)
    if filter_action:
        logs = logs.filter(action__icontains=filter_action)
    if filter_search:
        logs = logs.filter(
            Q(details__icontains=filter_search)
            | Q(object_repr__icontains=filter_search)
            | Q(object_id__icontains=filter_search)
        )
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)

    return logs


def _format_single_log(log):
    raw_details = str(log.details or "{}")

    try:
        changes_dict = json.loads(raw_details)
        if not isinstance(changes_dict, dict):
            changes_dict = {}
    except (ValueError, TypeError):
        changes_dict = {}

    model_class = log.content_type.model_class()
    target_table = (
        str(model_class._meta.verbose_name).capitalize()
        if model_class
        else log.content_type.model.capitalize()
    )

    translated_changes = {}
    for field, values in changes_dict.items():
        field_name = field
        if model_class:
            try:
                django_field = model_class._meta.get_field(field)
                field_name = str(django_field.verbose_name)
            except Exception:
                pass

        val_0 = _("Empty") if values[0] in ["Empty", "Vide"] else values[0]
        val_1 = _("Empty") if values[1] in ["Empty", "Vide"] else values[1]
        translated_changes[field_name] = [val_0, val_1]

    return {
        "date": log.created_at.strftime("%d/%m/%Y at %H:%M"),
        "action": log.action,
        "action_label": _(log.action),
        "target_table": target_table,
        "object_id": log.object_id,
        "object_label": log.object_repr,
        "changes": translated_changes,
        "user": str(log.user) if log.user else _("System"),
    }


def global_history_view(request):
    logs = GlobalAuditLog.objects.all().select_related("content_type", "user")

    logs = _apply_filters(logs, request)

    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    timeline = [_format_single_log(log) for log in page_obj]

    raw_content_types = ContentType.objects.filter(
        id__in=GlobalAuditLog.objects.values("content_type").distinct()
    )

    active_content_types = []
    for ctype in raw_content_types:
        model_class = ctype.model_class()
        model_name = (
            str(model_class._meta.verbose_name).capitalize()
            if model_class
            else ctype.model.capitalize()
        )
        active_content_types.append(
            {"model": ctype.model, "name": _(model_name)}
        )

    active_users = User.objects.filter(
        id__in=GlobalAuditLog.objects.values("user").distinct()
    )

    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    context = {
        "timeline": timeline,
        "page_obj": page_obj,
        "query_string": query_dict.urlencode(),
        "active_types": active_content_types,
        "active_users": active_users,
        "filters": {
            "type": request.GET.get("type", ""),
            "user": request.GET.get("user", ""),
            "action": request.GET.get("action", ""),
            "search": request.GET.get("search", ""),
            "date_from": request.GET.get("date_from", ""),
            "date_to": request.GET.get("date_to", ""),
        },
    }

    return render(request, "global_history.html", context)
