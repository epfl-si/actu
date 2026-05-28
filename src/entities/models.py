from django.db import models

from utils.models import LabelModel


class Entity(LabelModel):
    """
    Entity is a first-level LDAP group at EPFL

    For example : SV, SB, ENAC, ...
    """

    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    has_homepage = models.BooleanField(default=False)
