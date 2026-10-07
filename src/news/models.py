from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin
from entities.models import Entity
from news_formats.models import NewsFormat
from topics.models import Topic


class News(AuditModelMixin, models.Model):
    """
    A news contains properties related to a news.

    All translated news lives in NewsTranslation (translations app).
    """

    topics = models.ManyToManyField(
        Topic,
        related_name="news",
        verbose_name=_("Topics"),
        help_text=_("Topics related to this news."),
    )
    entities = models.ManyToManyField(
        Entity,
        blank=True,
        related_name="news",
        verbose_name=_("Entities"),
        help_text=_("Entities related to this news."),
    )
    format = models.ForeignKey(
        NewsFormat,
        on_delete=models.PROTECT,
        related_name="news",
        verbose_name=_("Format"),
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
    is_under_cc_license = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ["-created_at"]

    def __str__(self):
        return f"News #{self.pk}"

    def clean(self):
        super().clean()
        if self.pk is not None and not self.topics.exists():
            raise ValidationError(
                {"topics": _("A news must have at least one topic.")}
            )

    def get_translation(self, language):
        """Return the translation for this news, or None if it doesn't
        exist."""
        return self.translations.filter(language=language).first()
