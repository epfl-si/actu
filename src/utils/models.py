from django import utils
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _


def get_last_activity_label(instance):
    if instance.status == instance.Status.PUBLISHED:
        user = instance.published_by
        date = instance.published_at
        verb = _("Published on")
    elif instance.status == instance.Status.ARCHIVED:
        user = instance.updated_by
        date = instance.updated_at
        verb = _("Archived on")
    elif instance.updated_by:
        user = instance.updated_by
        date = instance.updated_at
        verb = _("Updated on")
    else:
        user = instance.created_by
        date = instance.created_at
        verb = _("Created on")

    user_name = f"{user.first_name} {user.last_name}" if user else ""

    if date is None:
        return f"{verb} — ({user_name})"
    date = localtime(date)

    return f"{verb} {date.strftime('%d.%m.%Y %H:%M')} ({user_name})"


class LabelModel(models.Model):
    label_fr = models.CharField(
        max_length=200,
        verbose_name=_("French"),
        help_text=_("Label in French"),
    )
    label_en = models.CharField(
        max_length=200,
        verbose_name=_("English"),
        help_text=_("Label in English"),
    )
    label_de = models.CharField(
        max_length=200,
        verbose_name=_("German"),
        help_text=_("Label in German"),
    )
    label_it = models.CharField(
        max_length=200,
        verbose_name=_("Italian"),
        help_text=_("Label in Italian"),
    )

    search_fields = [
        "label_en",
        "label_fr",
        "label_de",
        "label_it",
    ]

    def __str__(self):
        lang = utils.translation.get_language()
        return self.__getattribute__("label_" + lang)

    def get_label(self, lang):
        return self.__getattribute__("label_" + lang)

    class Meta:
        abstract = True
