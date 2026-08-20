from django.db import models
from django.utils.translation import gettext_lazy as _

from news.models import News


class Link(models.Model):
    """
    Link is a web link
    """

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    link = models.CharField(
        max_length=90,
        verbose_name=_("Link"),
    )
    news = models.ForeignKey(
        News,
        blank=True,
        related_name="news",
        verbose_name=_("News"),
        help_text=_("News related to this link."),
        on_delete=models.CASCADE,
    )
