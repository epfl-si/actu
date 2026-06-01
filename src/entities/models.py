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
            "Designates whether this entity is displayed on the main page."
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
