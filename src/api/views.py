from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.filters import EntityFilter, ThematicFilter
from api.pagination import NewsPagination
from api.serializers import (
    EntitySerializer,
    NewsSerializer,
    ThematicSerializer,
)
from entities.models import Entity
from thematics.models import Thematic
from translations.models import NewsTranslation


@extend_schema(tags=[_("Entities")])
@extend_schema_view(
    list=extend_schema(
        summary=_("List active entities"),
        description=_("Return all active entities ordered by identifier."),
    ),
    retrieve=extend_schema(
        summary=_("Retrieve an entity"),
        description=_("Return a single active entity by its identifier."),
    ),
)
class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Entity.objects.filter(is_active=True).order_by("id")
    serializer_class = EntitySerializer
    permission_classes = [AllowAny]
    filterset_class = EntityFilter


@extend_schema(tags=[_("Thematics")])
@extend_schema_view(
    list=extend_schema(
        summary=_("List active thematics"),
        description=_("Return all active thematics ordered by identifier."),
    ),
    retrieve=extend_schema(
        summary=_("Retrieve a thematic"),
        description=_("Return a single active thematic by its identifier."),
    ),
)
class ThematicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Thematic.objects.filter(is_active=True).order_by("id")
    serializer_class = ThematicSerializer
    permission_classes = [AllowAny]
    filterset_class = ThematicFilter


@extend_schema(tags=[_("News")])
@extend_schema_view(
    list=extend_schema(
        summary=_("List published news"),
        description=_(
            "Return published news, optionally filtered by a thematic, "
            "an entity, a language, or a title search."
        ),
        parameters=[
            OpenApiParameter(
                name="thematic",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_("Thematic identifier."),
            ),
            OpenApiParameter(
                name="entity",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_("Entity identifier."),
            ),
            OpenApiParameter(
                name="language",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_(
                    "Language code (en, fr, de, it). Defaults to the "
                    "request language."
                ),
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    _(
                        "Number of results per page. "
                        "Defaults to the API page size."
                    )
                ),
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_("Search in the news title."),
            ),
        ],
    ),
)
class NewsViewSet(viewsets.GenericViewSet):
    queryset = NewsTranslation.objects.none()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    pagination_class = NewsPagination

    def get_queryset(self):
        language = (
            self.request.query_params.get("language")
            or self.request.LANGUAGE_CODE
        )

        translations_qs = NewsTranslation.objects.filter(
            language=language,
            status=NewsTranslation.Status.PUBLISHED,
            published_at__isnull=False,
        )

        thematic_id = self.request.query_params.get("thematic")
        entity_id = self.request.query_params.get("entity")

        if thematic_id:
            translations_qs = translations_qs.filter(
                news__thematics__id=thematic_id,
            )
        elif entity_id:
            translations_qs = translations_qs.filter(
                news__entities__id=entity_id,
            )

        search = self.request.query_params.get("search")
        if search:
            translations_qs = translations_qs.filter(
                title__icontains=search.strip(),
            )

        return translations_qs.select_related("news").order_by("-published_at")

    def list(self, request, **kwargs):
        thematic_id = request.query_params.get("thematic")
        entity_id = request.query_params.get("entity")

        if thematic_id and entity_id:
            return Response(
                {"detail": _("Provide either thematic or entity, not both.")},
                status=400,
            )

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
