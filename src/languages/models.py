from django.db import models


class Language(models.Model):
    """
    Language is the list of available languages

    For example : en, fr
    """

    language = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.language
