import json

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver

from .middleware import current_user


class GlobalAuditLog(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="Object Type"
    )
    object_id = models.CharField(max_length=255, verbose_name="Object ID")

    object_repr = models.CharField(
        max_length=255, verbose_name="Object Name", default="Not defined"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    user = models.CharField(
        max_length=255, verbose_name="User", default="System"
    )

    action = models.CharField(max_length=100)
    details = models.TextField()

    class Meta:
        verbose_name = "Global log"
        verbose_name_plural = "Global Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} - {self.content_type} ({self.object_id})"


class AuditModelMixin(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_state = self._get_current_state()

    def _get_current_state(self):
        state = {}
        for field in self._meta.fields:
            if field.name == "id" or "password" in field.name.lower():
                continue
            try:
                val = getattr(self, field.name)
                state[field.name] = str(val) if val is not None else "Empty"
            except Exception:
                state[field.name] = "Error"
        return state

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        user_str = _get_user_str()

        super().save(*args, **kwargs)

        ctype = ContentType.objects.get_for_model(self)

        if is_new:
            self._just_created = True

            def make_create_log():
                modifs = {}
                new_state = self._get_current_state()
                for k, v in new_state.items():
                    if v != "Empty":
                        modifs[k] = ["", v]

                for m2m_field in self._meta.many_to_many:
                    m2m_objs = getattr(self, m2m_field.name).all()
                    if m2m_objs:
                        names = ", ".join(str(o) for o in m2m_objs)
                        modifs[m2m_field.name] = ["", names]

                GlobalAuditLog.objects.create(
                    content_type=ctype,
                    object_id=self.pk,
                    object_repr=str(self),
                    action="Create",
                    user=user_str,
                    details=json.dumps(modifs),
                )

            transaction.on_commit(make_create_log)

        else:
            new_state = self._get_current_state()
            modifs = {}

            for field, old_val in self._initial_state.items():
                new_val = new_state.get(field)
                if old_val != new_val:
                    modifs[field] = [old_val, new_val]

            if modifs:
                GlobalAuditLog.objects.create(
                    content_type=ctype,
                    object_id=self.pk,
                    object_repr=str(self),
                    action="Edit",
                    user=user_str,
                    details=json.dumps(modifs),
                )

        self._initial_state = self._get_current_state()


def _get_user_str():
    user = current_user.get()
    return str(user) if user and user.is_authenticated else "System"


def _get_m2m_field_name(instance, sender):
    for field in instance._meta.many_to_many:
        if field.remote_field.through == sender:
            return field.name
    return "Relation"


def _save_m2m_audit_log(instance, field_name):
    new_objects = list(getattr(instance, field_name).all())
    new_names = ", ".join(str(o) for o in new_objects) or "Empty"
    old_names = instance._m2m_memory.get(field_name, "Empty")

    if old_names != new_names:
        user_str = _get_user_str()
        ctype = ContentType.objects.get_for_model(instance)
        modifs = {field_name: [old_names, new_names]}

        GlobalAuditLog.objects.create(
            content_type=ctype,
            object_id=instance.pk,
            object_repr=str(instance),
            action="Edit",
            user=user_str,
            details=json.dumps(modifs),
        )

    if field_name in instance._m2m_memory:
        del instance._m2m_memory[field_name]


@receiver(m2m_changed)
def audit_m2m_changed(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if not hasattr(instance, "_initial_state") or reverse:
        return

    if getattr(instance, "_just_created", False):
        return

    if action not in ["pre_clear", "pre_add", "pre_remove"]:
        return

    field_name = _get_m2m_field_name(instance, sender)

    if not hasattr(instance, "_m2m_memory"):
        instance._m2m_memory = {}

    if field_name not in instance._m2m_memory:
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

        GlobalAuditLog.objects.create(
            content_type=ctype,
            object_id=instance.pk,
            object_repr=str(instance),
            action="Delete",
            user=user_str,
            details="{}",
        )
