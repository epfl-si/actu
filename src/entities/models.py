from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import LabelModel


class Entity(LabelModel):
    """
    Entity is a first-level LDAP group at EPFL

    For example : SV, SB, ENAC, ...
    """

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")
        constraints = [
            models.CheckConstraint(
                check=models.Q(has_homepage=False) | ~models.Q(slug=''),
                name='entity_slug_required_if_has_homepage'
            )
        ]

    slug = models.SlugField(
        max_length=200,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Define the Slug of this Entity"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether this entity is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main"),
        help_text=_(
            "Designates whether this entity (School) is displayed on the "
            "footer."
        ),
    )
    has_homepage = models.BooleanField(
        default=False,
        verbose_name=_("Has Homepage"),
        help_text=_(
            "Designates whether this entity has a dedicated homepage."
        ),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_(
            "Defines the display order. A value of 0 means that the order "
            "is ignored (for non-main entities)."
        ),
    )

    def clean(self):
        super().clean()

        if self.has_homepage and not self.slug:
            raise ValidationError({
                'slug': _("The slug is required when 'Has Homepage' is checked.")
            })

        if not self.has_homepage and self.slug:
            raise ValidationError({
                'slug': _("The slug must be empty if 'Has Homepage' is not checked.")
            })
