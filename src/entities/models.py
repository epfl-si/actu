from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from translations.models import Translation


class Entity(models.Model):
    """
    Entity is a first-level LDAP group at EPFL

    For example : SV, SB, ENAC, ...
    """

    label = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    has_homepage = models.BooleanField(default=False)
    translations = GenericRelation(Translation)

    def __str__(self):
        return self.label
