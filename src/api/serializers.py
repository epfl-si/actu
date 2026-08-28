from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from entities.models import Entity
from thematics.models import Thematic


@extend_schema_serializer(
    component_name="Entity",
    examples=[
        OpenApiExample(
            "Main entity",
            value={
                "id": 1,
                "label_fr": "Faculté des sciences",
                "label_en": "School of Science",
                "label_de": "Naturwissenschaftliche Fakultät",
                "label_it": "Facoltà di scienze",
                "is_main": True,
                "order": 1,
            },
        ),
    ],
)
class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity
        fields = [
            "id",
            "label_fr",
            "label_en",
            "label_de",
            "label_it",
            "is_main",
            "order",
        ]
        extra_kwargs = {
            "id": {"help_text": _("Unique identifier of the entity.")},
            "is_main": {
                "help_text": _("Whether this entity is marked as main.")
            },
            "order": {
                "help_text": _(
                    "Display order of the entity among main entities."
                )
            },
        }


@extend_schema_serializer(
    component_name="Thematic",
    examples=[
        OpenApiExample(
            "Main thematic",
            value={
                "id": 1,
                "label_fr": "Intelligence artificielle",
                "label_en": "Artificial intelligence",
                "label_de": "Künstliche Intelligenz",
                "label_it": "Intelligenza artificiale",
                "is_main": True,
                "order": 1,
            },
        ),
    ],
)
class ThematicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Thematic
        fields = [
            "id",
            "label_fr",
            "label_en",
            "label_de",
            "label_it",
            "is_main",
            "order",
        ]
        extra_kwargs = {
            "id": {"help_text": _("Unique identifier of the thematic.")},
            "is_main": {
                "help_text": _("Whether this thematic is marked as main.")
            },
            "order": {"help_text": _("Display order of the thematic.")},
        }
