from django.conf import settings
from django.db import models
from django.db.models.fields import URLField
from django.utils.translation import gettext_lazy as _

from news.models import News


class NewsLink(models.Model):
    """
    Links of a news item.
    """

    class Meta:
        verbose_name = _("News link")
        verbose_name_plural = _("News links")

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name=_("News"),
    )
    language = models.CharField(
        max_length=2, choices=settings.LANGUAGES, verbose_name=_("Language")
    )
    link = URLField(
        max_length=512,
        verbose_name=_("Link"),
    )

    def __str__(self):
        return f"{self.link} [{self.language}]"
