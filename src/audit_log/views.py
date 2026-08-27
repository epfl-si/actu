from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _

from .models import GlobalAuditLog


def _clean_date(date_str):
    if not date_str:
        return ""
    try:
        return date_str if parse_date(date_str) else ""
    except ValueError:
        return ""


def _get_filters(request):
    return {
        "type": request.GET.getlist("type"),
        "user": request.GET.getlist("user"),
        "action": request.GET.getlist("action"),
        "search": request.GET.get("search", "").strip(),
        "from": _clean_date(request.GET.get("from")),
        "to": _clean_date(request.GET.get("to")),
    }


def _apply_filters(logs, filters):
    filter_type = filters.get("type")
    filter_user = filters.get("user")
    filter_action = filters.get("action")
    filter_search = filters.get("search")
    date_from = filters.get("from")
    date_to = filters.get("to")

    if filter_type:
        logs = logs.filter(content_type__model__in=filter_type)
    if filter_user:
        logs = logs.filter(user__in=filter_user)
    if filter_action:
        logs = logs.filter(action__in=filter_action)

    if filter_search:
        logs = logs.filter(
            Q(details__icontains=filter_search)
            | Q(object_repr__icontains=filter_search)
            | Q(user__icontains=filter_search)
        )

    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)

    return logs


def _format_single_log(log):
    changes_dict = log.details

    if not isinstance(changes_dict, dict):
        changes_dict = {}

    model_class = log.content_type.model_class()
    target_table = (
        str(model_class._meta.verbose_name)
        if model_class
        else log.content_type.model
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

        val_0 = _("Empty") if values[0] == "Empty" else values[0]
        val_1 = _("Empty") if values[1] == "Empty" else values[1]
        translated_changes[field_name] = [val_0, val_1]

    return {
        "id": log.id,
        "date": timezone.localtime(log.created_at).strftime("%d/%m/%Y %H:%M"),
        "user": log.user,
        "action": log.action,
        "action_label": _(log.action),
        "type": target_table,
        "subject": log.object_repr,
        "changes": translated_changes,
    }


@login_required
def global_history_view(request):
    if not request.user.is_superuser or not request.user.is_active:
        raise PermissionDenied

    filters = _get_filters(request)
    logs = GlobalAuditLog.objects.all().select_related("content_type")
    logs = _apply_filters(logs, filters)

    paginator = Paginator(logs, 30)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1
    )

    timeline = [_format_single_log(log) for log in page_obj]

    raw_content_types = ContentType.objects.filter(
        id__in=GlobalAuditLog.objects.values("content_type").distinct()
    )

    active_content_types = []
    for ctype in raw_content_types:
        model_class = ctype.model_class()
        model_name = (
            str(model_class._meta.verbose_name) if model_class else ctype.model
        )
        active_content_types.append(
            {"model": ctype.model, "name": _(model_name)}
        )

    active_users = (
        GlobalAuditLog.objects.exclude(user="")
        .order_by("user")
        .values_list("user", flat=True)
        .distinct()
    )

    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    context = {
        "timeline": timeline,
        "page_obj": page_obj,
        "page_range": page_range,
        "paginator": paginator,
        "query_string": query_dict.urlencode(),
        "active_types": active_content_types,
        "active_users": active_users,
        "filters": filters,
    }

    return render(request, "global_history.html", context)
