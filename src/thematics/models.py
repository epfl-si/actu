from django.db import models

from utils.models import LabelModel


class Thematic(LabelModel):
    """
    Thematic is a topic

    For example : AI, Health, Energy, ...
    """

    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    has_homepage = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True)
