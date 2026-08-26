from django.db import models
from django.utils.translation import gettext_lazy as _

from block_types.models import BlockType
from utils.models import LabelModel


class NewsFormat(LabelModel):
    icon = models.CharField(max_length=255, blank=True, null=True)
    allowed_blocks = models.ManyToManyField(
        BlockType,
        blank=True,
        related_name="news_formats",
    )

    class Meta:
        db_table = "news_formats"
        verbose_name = _("News Format")
        verbose_name_plural = _("News Formats")
