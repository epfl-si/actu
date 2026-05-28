from django import utils
from django.db import models


class LabelModel(models.Model):
    label_fr = models.CharField(max_length=100)
    label_en = models.CharField(max_length=100)
    label_de = models.CharField(max_length=100)
    label_it = models.CharField(max_length=100)

    def str(self):
        lang = utils.translation.get_language()
        return self.__getattribute__("label_" + lang)

    def get_label(self, lang):
        return self.__getattribute__("label_" + lang)

    class Meta:
        abstract = True
