from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from languages.models import Language


class Translation(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # virtual field

    language =  models.ForeignKey(Language, on_delete=models.CASCADE)
    translation = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['object_id', 'content_type', 'language'],
                name='unique_translation_per_object_language'
            )
        ]
