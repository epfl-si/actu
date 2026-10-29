from io import BytesIO
from typing import Literal

import PIL.Image
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin
from news.models import News


class ImageRenderingError(Exception):
    """The image file cannot be decoded or rendered."""


def news_image_upload_path(instance, filename):
    """Return the upload path for a news image, grouped by news id."""
    return f"news/images/{instance.news_id}/{filename}"


class NewsImage(AuditModelMixin, models.Model):
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
        upload_to=news_image_upload_path,
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

    def render(self, resolution: Literal["full"] | tuple[int, int]) -> bytes:
        """Render this image as progressive JPEG quality 90 bytes.

        "full" renders at the source dimensions — still re-encoded.
        A (width, height) tuple applies the stored crop (when set)
        and fits the result within the box, never upscaling.

        Raises ImageRenderingError if the file cannot be rendered.
        """
        try:
            image_file = self.image.open("rb")
            try:
                image = PIL.Image.open(image_file)
                image.load()
            finally:
                image_file.close()
        except (
            OSError,
            ValueError,
            PIL.Image.DecompressionBombError,
        ) as error:
            raise ImageRenderingError(
                "Image file cannot be rendered."
            ) from error

        if resolution != "full":
            if all(
                getattr(self, f"crop_{part}") is not None
                for part in ("left", "upper", "right", "lower")
            ):
                image = image.crop(
                    (
                        self.crop_left,
                        self.crop_upper,
                        self.crop_right,
                        self.crop_lower,
                    )
                )

            image.thumbnail(resolution, PIL.Image.Resampling.LANCZOS)

        image = _flatten_on_white(image)

        buffer = BytesIO()
        image.save(buffer, "jpeg", optimize=True, quality=90, progressive=True)
        return buffer.getvalue()


def _flatten_on_white(image: PIL.Image.Image):
    """Convert an image to RGB, compositing transparency on white.

    JPEG has no alpha: RGBA, LA and P images are composited on white
    so transparent areas do not render black (a plain convert("RGB")
    drops the alpha without compositing).
    """
    if image.mode == "RGB":
        return image
    if image.mode not in ("RGBA", "LA", "P"):
        return image.convert("RGB")

    background = PIL.Image.new("RGB", image.size, (255, 255, 255))
    rgba = image.convert("RGBA")
    background.paste(rgba, mask=rgba.split()[-1])
    return background


@receiver(pre_save, sender=NewsImage)
def delete_old_image_file(sender, instance, **kwargs):
    """Delete the previous image file when a new one is uploaded."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = old_instance.image
    new_file = instance.image

    if old_file and old_file.name and old_file.name != new_file.name:
        old_file.delete(save=False)


@receiver(post_delete, sender=NewsImage)
def delete_image_file(sender, instance, **kwargs):
    """Delete the image file when the NewsImage instance is deleted."""
    if instance.image:
        instance.image.delete(save=False)
