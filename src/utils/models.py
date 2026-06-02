from django import utils
from django.db import models
from django.utils.translation import gettext_lazy as _


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
