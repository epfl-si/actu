from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from translations.models import Translation


class Thematic(models.Model):
    """
    Thematic is a topic

    For example : AI, Health, Energy, ...
    """

    label = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    has_homepage = models.BooleanField(default=True)
    order = models.IntegerField()
    translations = GenericRelation(Translation)

    def __str__(self):
        return self.label
