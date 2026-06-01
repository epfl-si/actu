from django.db import models

from utils.models import LabelModel


class Thematic(LabelModel):
    """
    Thematic is a topic

    For example : AI, Health, Energy, ...
    """

    is_active = models.BooleanField(
        default=True,
        verbose_name=("Active"),
        help_text=(
            "Designates whether this thematic is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=("Main"),
        help_text=(
            "Designates whether this thematic is displayed on the main page."
        ),
    )
    has_homepage = models.BooleanField(
        default=False,
        verbose_name=("Has Homepage"),
        help_text=(
            "Designates whether this thematic has a dedicated homepage."
        ),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=("Order"),
        help_text=(
            "Defines the display order. A value of 0 means the thematic "
            "is hidden."
        ),
    )
