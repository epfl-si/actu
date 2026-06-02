from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import LabelModel


class Thematic(LabelModel):
    """
    Thematic is a topic

    For example : AI, Health, Energy, ...
    """

    class Meta:
        verbose_name = _("Thematic")
        verbose_name_plural = _("Thematics")

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether this thematic is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main"),
        help_text=_(
            "Designates whether this thematic is displayed on the main menu."
        ),
    )
    has_homepage = models.BooleanField(
        default=False,
        verbose_name=_("Has Homepage"),
        help_text=_(
            "Designates whether this thematic has a dedicated homepage."
        ),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Defines the display order."),
    )
