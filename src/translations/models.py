from django.conf import settings
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from news.models import News


class NewsTranslation(models.Model):
    """
    Translations of a news item.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        ARCHIVED = "archived", _("Archived")

    class Meta:
        verbose_name = _("News translation")
        verbose_name_plural = _("News translations")
        constraints = [
            models.UniqueConstraint(
                fields=["news", "language"],
                name="unique_translation_per_language",
            )
        ]
        ordering = ["-created_at"]

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name=_("News"),
    )
    language = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        verbose_name=_("Language"),
    )
    title = models.CharField(
        max_length=90,
        verbose_name=_("Title"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Status"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="translations_created",
        verbose_name=_("Created by"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="translations_updated",
        verbose_name=_("Updated by"),
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published at"),
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="translations_published",
        verbose_name=_("Published by"),
    )

    def __str__(self):
        return f"{self.title} [{self.language}]"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def last_activity_label(self):
        """
        Returns a human-readable string describing the last
        meaningful action on this translation.
        """
        if self.status == self.Status.PUBLISHED:
            user = self.published_by
            date = self.published_at
            verb = _("Published on")
        elif self.status == self.Status.ARCHIVED:
            user = self.updated_by
            date = self.updated_at
            verb = _("Archived on")
        else:
            if self.updated_by:
                user = self.updated_by
                date = self.updated_at
                verb = _("Updated on")
            else:
                user = self.created_by
                date = self.created_at
                verb = _("Created on")

        user_name = f"{user.first_name} {user.last_name}" if user else ""

        if date is None:
            return f"{verb} — ({user_name})"
        date = localtime(date)

        return f"{verb} {date.strftime('%d.%m.%Y %H:%M')} ({user_name})"
