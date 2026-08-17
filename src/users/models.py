from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin


class User(AuditModelMixin, AbstractUser):
    sciper = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.sciper})"
