from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from entities.models import Entity
from thematics.models import Thematic


class News(models.Model):
    """
    A news contains properties related to a news.

    All translated news lives in NewsTranslation (translations app).
    """

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ["-created_at"]

    thematics = models.ManyToManyField(
        Thematic,
        blank=True,
        related_name="news",
        verbose_name=_("Thematics"),
        help_text=_("Thematics related to this news."),
    )
    entities = models.ManyToManyField(
        Entity,
        blank=True,
        related_name="news",
        verbose_name=_("Entities"),
        help_text=_("Entities related to this news."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="news_created",
        verbose_name=_("Created by"),
    )

    def __str__(self):
        return f"News #{self.pk}"
