import json

from django.contrib.contenttypes.models import ContentType

from .models import GlobalAuditLog


def log_action(user, obj, action, details_dict=None):
    """
    Function to manually create a log from any view.
    details_dict must be a dictionary: {"Title": ["Old", "New"]}
    """
    ctype = ContentType.objects.get_for_model(obj)

    details_json = json.dumps(details_dict) if details_dict else "{}"

    GlobalAuditLog.objects.create(
        content_type=ctype,
        object_id=obj.pk,
        object_repr=str(obj),
        action=action,
        user=user if user.is_authenticated else None,
        details=details_json,
    )
