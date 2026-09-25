from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from news.models import News


class NewsImage(models.Model):
    """
    An image attached to a news item.

    Images live in a single pool per news and can be reused as the visual,
    images to download or inside dynamic blocks.
    """

    class Meta:
        verbose_name = _("News image")
        verbose_name_plural = _("News images")
        ordering = ["-created_at"]

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("News"),
    )
    image = models.ImageField(
        upload_to="news/images/",
        verbose_name=_("Image"),
    )

    alt_text_fr = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Alt text (FR)"),
    )
    alt_text_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Alt text (EN)"),
    )
    alt_text_de = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Alt text (DE)"),
    )
    alt_text_it = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Alt text (IT)"),
    )

    caption_fr = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Caption (FR)"),
    )
    caption_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Caption (EN)"),
    )
    caption_de = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Caption (DE)"),
    )
    caption_it = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Caption (IT)"),
    )

    author = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Author"),
    )
    rights = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Rights"),
    )

    crop_left = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Crop left"),
    )
    crop_upper = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Crop upper"),
    )
    crop_right = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Crop right"),
    )
    crop_lower = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Crop lower"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="news_images_created",
        verbose_name=_("Created by"),
    )

    def __str__(self):
        return f"Image #{self.pk} ({self.image.name or '-'})"

    def get_alt_text(self, language):
        """Return the alt text for the given language, falling back to EN."""
        return getattr(self, f"alt_text_{language}", "") or self.alt_text_en

    def get_caption(self, language):
        """Return the caption for the given language, falling back to EN."""
        return getattr(self, f"caption_{language}", "") or self.caption_en
