from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from .middleware import current_user


class AuditQuerySet(models.QuerySet):
    def bulk_create(self, objs, *args, **kwargs):
        created_objs = super().bulk_create(objs, *args, **kwargs)

        if not created_objs:
            return created_objs

        ctype = ContentType.objects.get_for_model(created_objs[0])
        user_str = _get_user_str()
        logs = []

        for obj in created_objs:
            current_state = obj._get_current_state()

            formatted_details = {
                field: ["", _get_readable_value(obj.__class__, field, value)]
                for field, value in current_state.items()
            }

            logs.append(
                GlobalAuditLog(
                    content_type=ctype,
                    object_id=str(obj.pk),
                    object_repr=str(obj),
                    action="Create",
                    user=user_str,
                    details=formatted_details,
                )
            )

        GlobalAuditLog.objects.bulk_create(logs)

        return created_objs

    def bulk_update(self, objs, fields, batch_size=None):
        pks = [obj.pk for obj in objs]
        old_objs = {
            obj.pk: obj for obj in self.model.objects.filter(pk__in=pks)
        }

        ctype = ContentType.objects.get_for_model(self.model)
        logs = []

        for obj in objs:
            old_obj = old_objs.get(obj.pk)
            if not old_obj:
                continue

            changes = {}
            for field in fields:
                old_val = str(getattr(old_obj, field, ""))
                new_val = str(getattr(obj, field, ""))

                if old_val != new_val:
                    readable_old = _get_readable_value(
                        obj.__class__, field, old_val
                    )
                    readable_new = _get_readable_value(
                        obj.__class__, field, new_val
                    )
                    changes[field] = [readable_old, readable_new]

            user_str = _get_user_str()
            if changes:
                logs.append(
                    GlobalAuditLog(
                        content_type=ctype,
                        object_id=str(obj.pk),
                        object_repr=str(obj),
                        action="Edit",
                        user=user_str,
                        details=changes,
                    )
                )

        if logs:
            GlobalAuditLog.objects.bulk_create(logs)

        return super().bulk_update(objs, fields, batch_size=batch_size)


class GlobalAuditLog(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Object Type"),
    )
    object_id = models.CharField(max_length=255, verbose_name=_("Object ID"))

    object_repr = models.CharField(
        max_length=500, verbose_name=_("Object Name"), default=_("Not defined")
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date")
    )

    user = models.CharField(
        max_length=500, verbose_name=_("User"), default=_("System")
    )

    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)

    class Meta:
        verbose_name = _("Global log")
        verbose_name_plural = _("Global Logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["-created_at"], name="audit_g_created_at_idx"
            ),
            models.Index(
                fields=["content_type", "object_id", "-created_at"],
                name="audit_g_ct_obj_idx",
            ),
            models.Index(
                fields=["user", "-created_at"], name="audit_g_user_idx"
            ),
        ]

    def __str__(self):
        return f"{self.created_at} - {self.content_type} ({self.object_id})"


class AuditModelMixin(models.Model):
    objects = AuditQuerySet.as_manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_state = self._get_current_state()

    def _get_current_state(self):
        state = {}
        with override("en"):
            for field in self._meta.fields:
                if field.name == "id" or "password" in field.name.lower():
                    continue
                try:
                    val = field.value_from_object(self)
                    state[field.name] = (
                        str(val) if val is not None else "Empty"
                    )
                except Exception:
                    state[field.name] = "Error"
        return state

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        user_str = _get_user_str()

        super().save(*args, **kwargs)

        ctype = ContentType.objects.get_for_model(self)

        if is_new:

            def make_create_log():
                with override("en"):
                    modifs = {}
                    new_state = self._get_current_state()
                    for k, v in new_state.items():
                        if v != "Empty":
                            readable_v = _get_readable_value(
                                self.__class__, k, v
                            )
                            modifs[k] = ["", readable_v]

                    GlobalAuditLog.objects.create(
                        content_type=ctype,
                        object_id=str(self.pk),
                        object_repr=str(self),
                        action="Create",
                        user=user_str,
                        details=modifs,
                    )

            transaction.on_commit(make_create_log)
        else:
            new_state = self._get_current_state()
            modifs = {}

            for field, old_val in self._initial_state.items():
                new_val = new_state.get(field)
                if old_val != new_val:
                    readable_old = _get_readable_value(
                        self.__class__, field, old_val
                    )
                    readable_new = _get_readable_value(
                        self.__class__, field, new_val
                    )
                    modifs[field] = [readable_old, readable_new]

            if modifs:

                def make_edit_log():
                    with override("en"):
                        GlobalAuditLog.objects.create(
                            content_type=ctype,
                            object_id=str(self.pk),
                            object_repr=str(self),
                            action="Edit",
                            user=user_str,
                            details=modifs,
                        )

                transaction.on_commit(make_edit_log)

        self._initial_state = self._get_current_state()


def _get_user_str():
    user = current_user.get()
    return str(user) if user and user.is_authenticated else "System"


def _get_readable_value(model_class, field_name, raw_value):
    """Translate an ID in a readable name (ex: '4' -> 'Health')"""
    if raw_value in ["Empty", "Error", "", None]:
        return str(raw_value) if raw_value is not None else "Empty"

    try:
        field = model_class._meta.get_field(field_name)
        if field.is_relation and field.related_model:
            rel_obj = field.related_model.objects.filter(pk=raw_value).first()
            if rel_obj:
                return str(rel_obj)
    except Exception:
        pass

    return str(raw_value)
