from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    sciper = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.sciper})"
