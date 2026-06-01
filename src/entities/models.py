from django.db import models

from utils.models import LabelModel


class Entity(LabelModel):
    """
    Entity is a first-level LDAP group at EPFL

    For example : SV, SB, ENAC, ...
    """

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    is_active = models.BooleanField(
        default=True,
        verbose_name=("Active"),
        help_text=(
            "Designates whether this entity is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=("Main"),
        help_text=(
            "Designates whether this entity is displayed on the main page."
        ),
    )
    has_homepage = models.BooleanField(
        default=False,
        verbose_name=("Has Homepage"),
        help_text=("Designates whether this entity has a dedicated homepage."),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=("Order"),
        help_text=(
            "Defines the display order. A value of 0 means that the order "
            "is ignored (for non-main entities)."
        ),
    )
