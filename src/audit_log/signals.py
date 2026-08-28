from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.utils.translation import override

from .models import (
    AuditModelMixin,
    GlobalAuditLog,
    _get_user_str,
)


def _save_m2m_audit_log(instance, field_name):
    with override("en"):
        new_objects = list(getattr(instance, field_name).all())
        new_names = ", ".join(str(o) for o in new_objects) or "Empty"
        old_names = getattr(instance, "_m2m_memory", {}).get(
            field_name, "Empty"
        )

        if old_names != new_names:
            user_str = _get_user_str()
            ctype = ContentType.objects.get_for_model(instance)
            modifs = {field_name: [old_names, new_names]}

            GlobalAuditLog.objects.create(
                content_type=ctype,
                object_id=str(instance.pk),
                object_repr=str(instance),
                action="Edit",
                user=user_str,
                details=modifs,
            )

    if field_name in getattr(instance, "_m2m_memory", {}):
        del instance._m2m_memory[field_name]


@receiver(m2m_changed)
def audit_m2m_changed(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if action not in ["pre_clear", "pre_add", "pre_remove"]:
        return

    if reverse:
        if issubclass(model, AuditModelMixin) and pk_set:
            for obj in model.objects.filter(pk__in=pk_set):
                field_name = _get_m2m_field_name(obj, sender)
                transaction.on_commit(
                    lambda o=obj, f=field_name: _save_m2m_audit_log(o, f)
                )
        return

    if not hasattr(instance, "_initial_state"):
        return

    field_name = _get_m2m_field_name(instance, sender)

    if not hasattr(instance, "_m2m_memory"):
        instance._m2m_memory = {}

    if field_name not in instance._m2m_memory:
        with override("en"):
            old_objects = list(getattr(instance, field_name).all())
            instance._m2m_memory[field_name] = (
                ", ".join(str(o) for o in old_objects) or "Empty"
            )

        transaction.on_commit(
            lambda: _save_m2m_audit_log(instance, field_name)
        )


@receiver(pre_delete)
def audit_delete_log(sender, instance, **kwargs):
    if isinstance(instance, AuditModelMixin):
        user_str = _get_user_str()
        ctype = ContentType.objects.get_for_model(instance)

        with override("en"):
            GlobalAuditLog.objects.create(
                content_type=ctype,
                object_id=str(instance.pk),
                object_repr=str(instance),
                action="Delete",
                user=user_str,
                details={},
            )


def _get_m2m_field_name(instance, sender):
    for field in instance._meta.many_to_many:
        if field.remote_field.through == sender:
            return field.name
    return "Unknown relation"
