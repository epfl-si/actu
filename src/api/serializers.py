from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from entities.models import Entity
from thematics.models import Thematic
from translations.models import NewsTranslation


@extend_schema_serializer(
    component_name="News",
    examples=[
        OpenApiExample(
            "News item",
            value={
                "id": 42,
                "title": "Sample news title",
                "format": "News",
            },
        ),
    ],
)
class NewsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="news.id",
        read_only=True,
        help_text=_("Unique identifier of the news item."),
    )
    format = serializers.SerializerMethodField(
        help_text=_("Format of the news item in the requested language."),
    )

    class Meta:
        model = NewsTranslation
        fields = ["id", "title", "format"]

    def get_format(self, obj: NewsTranslation) -> str:
        return obj.news.format.get_label(obj.language)


class LabelModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "label_fr",
            "label_en",
            "label_de",
            "label_it",
            "is_main",
            "order",
        ]


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
class EntitySerializer(LabelModelSerializer):
    class Meta(LabelModelSerializer.Meta):
        model = Entity
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
class ThematicSerializer(LabelModelSerializer):
    class Meta(LabelModelSerializer.Meta):
        model = Thematic
        extra_kwargs = {
            "id": {"help_text": _("Unique identifier of the thematic.")},
            "is_main": {
                "help_text": _("Whether this thematic is marked as main.")
            },
            "order": {"help_text": _("Display order of the thematic.")},
        }
