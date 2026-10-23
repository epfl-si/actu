from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import NewsImage


@extend_schema_serializer(
    component_name="NewsImage",
    examples=[
        OpenApiExample(
            "News image",
            value={
                "id": 1,
                "image": "/uploads/news/images/42/sample.jpg",
                "alt_text_fr": "Texte alternatif",
                "alt_text_en": "Alt text",
                "alt_text_de": "Alt-Text",
                "alt_text_it": "Testo alternativo",
                "caption_fr": "Légende",
                "caption_en": "Caption",
                "caption_de": "Bildunterschrift",
                "caption_it": "Didascalia",
                "author": "Author name",
                "rights": "EPFL",
                "crop_left": 0,
                "crop_upper": 0,
                "crop_right": 1600,
                "crop_lower": 900,
                "created_at": "2026-09-29T12:00:00Z",
            },
        ),
    ],
)
class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = [
            "id",
            "image",
            "alt_text_fr",
            "alt_text_en",
            "alt_text_de",
            "alt_text_it",
            "caption_fr",
            "caption_en",
            "caption_de",
            "caption_it",
            "author",
            "rights",
            "crop_left",
            "crop_upper",
            "crop_right",
            "crop_lower",
            "created_at",
        ]
