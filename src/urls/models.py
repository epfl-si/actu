from django.db import models
from django.db.models.fields import URLField
from django.utils.translation import gettext_lazy as _

from translations.models import NewsTranslation


class NewsUrl(models.Model):
    """
    URLs of a news item.
    """

    class Meta:
        verbose_name = _("News URL")
        verbose_name_plural = _("News URLs")

    translation = models.ForeignKey(
        NewsTranslation,
        on_delete=models.CASCADE,
        related_name="urls",
        verbose_name=_("Translation"),
    )
    url = URLField(
        max_length=512,
        verbose_name=_("URL"),
    )

    def __str__(self):
        return f"{self.url}"
