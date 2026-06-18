from django.core.exceptions import ValidationError
from django.db import models
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
