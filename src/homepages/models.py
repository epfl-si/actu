from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _


class Homepage(models.Model):

    class Meta:
        verbose_name = _("Homepage")
        verbose_name_plural = _("Homepages")

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(thematic__isnull=True, entity__isnull=False)
                    | models.Q(thematic__isnull=False, entity__isnull=True)
                ),
                name="homepage_must_have_exactly_one_relation",
            )
        ]

    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Define the Slug of this Homepage"),
    )

    thematic = models.OneToOneField(
        "thematics.Thematic",
        on_delete=models.CASCADE,
        related_name="homepage",
        null=True,
        blank=True,
        verbose_name=_("Thematic"),
    )

    entity = models.OneToOneField(
        "entities.Entity",
        on_delete=models.CASCADE,
        related_name="homepage",
        null=True,
        blank=True,
        verbose_name=_("Entity"),
    )

    users = models.ManyToManyField(
        "users.User",
        related_name="homepages",
        blank=True,
        verbose_name=_("Users"),
    )

    @property
    def display_name(self):
        if self.thematic:
            return str(self.thematic)
        return str(self.entity)

    def clean(self):
        super().clean()

        if self.thematic and self.entity:
            raise ValidationError(
                _(
                    "A Homepage cannot be linked to both a "
                    "thematic and an entity."
                )
            )

        if not self.thematic and not self.entity:
            raise ValidationError(
                _(
                    "A Homepage must be linked to either a "
                    "thematic or an entity."
                )
            )


class HomepageTranslation(models.Model):
    """
    Translations of a homepage item.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        ARCHIVED = "archived", _("Archived")

    class Meta:
        verbose_name = _("Homepage translation")
        verbose_name_plural = _("Homepage translations")
        constraints = [
            models.UniqueConstraint(
                fields=["homepage", "language"],
                name="unique_homepage_translation_per_language",
            )
        ]
        ordering = ["-created_at"]

    homepage = models.ForeignKey(
        Homepage,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name=_("Homepage"),
    )
    language = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        verbose_name=_("Language"),
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
        related_name="homepage_translations_created",
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
        related_name="homepage_translations_updated",
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
        related_name="homepage_translations_published",
        verbose_name=_("Published by"),
    )

    def __str__(self):
        return f"{self.homepage.display_name} [{self.language}]"

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

        date = localtime(date)
        user_name = f"{user.first_name} {user.last_name}" if user else ""

        return f"{verb} {date.strftime('%d.%m.%Y %H:%M')} ({user_name})"
