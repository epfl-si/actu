from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin
from news.models import News
from utils.models import get_last_activity_label


class NewsTranslation(AuditModelMixin, models.Model):
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
    slug = AutoSlugField(
        populate_from="title",
        max_length=255,
        unique=True,
        always_update=True,
        null=True,
        blank=True,
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
        return get_last_activity_label(instance=self)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_slug = self.slug

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self._original_slug and self._original_slug != self.slug:
            NewsSlugHistory.objects.get_or_create(
                news_translation_id=self.pk,
                old_slug=self._original_slug,
            )
            NewsSlugHistory.objects.filter(
                news_translation_id=self.pk,
                old_slug=self.slug,
            ).delete()

        self._original_slug = self.slug


class NewsSlugHistory(models.Model):
    news_translation = models.ForeignKey(
        "NewsTranslation",
        on_delete=models.CASCADE,
        related_name="historical_slugs",
    )
    old_slug = models.CharField(max_length=255, db_index=True, unique=True)
