from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from news.models import News


class NewsMultiRef(models.Model):
    """
    multi-reference for [links|files|images] of a news item.
    """

    class Type(models.TextChoices):
        LINK = "link", _("Link")
        FILE = "file", _("File")
        IMAGE = "image", _("Image")

    class Meta:
        verbose_name = _("News multi-reference")
        verbose_name_plural = _("News multi-references")

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="multirefs",
        verbose_name=_("News"),
    )
    language = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        verbose_name=_("Language"),
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name=_("Type"),
    )
    ref = models.CharField(
        max_length=512,
        verbose_name=_("Ref"),
    )

    def __str__(self):
        return f"{self.ref} [{self.language}]"

    @classmethod
    def get_files(cls, news_id):
        return NewsMultiRef.objects.filter(news_id=news_id, type=cls.Type.FILE)

    @classmethod
    def get_images(cls, news_id):
        return NewsMultiRef.objects.filter(
            news_id=news_id, type=cls.Type.IMAGE
        )

    @classmethod
    def get_links(cls, news_id, language):
        return NewsMultiRef.objects.filter(
            news_id=news_id, type=cls.Type.LINK, language=language
        )
