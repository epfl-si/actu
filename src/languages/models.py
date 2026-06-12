from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import LabelModel


class Language(LabelModel):
    """
    News and content language available (fr, en, de, it).
    """

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ["code"]

    code = models.CharField(
        max_length=2,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("Language code (e.g. 'fr', 'en', 'de', 'it')."),
    )
