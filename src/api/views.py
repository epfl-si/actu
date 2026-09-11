from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

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


def _parse_id_list(query_params, key):
    """Return a list of ints for the key, or None if any value is invalid."""
    try:
        return [int(value) for value in query_params.getlist(key) if value]
    except ValueError:
        return None


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
            "Return published news, optionally filtered by thematic "
            "identifiers, entity identifiers, format identifiers, a "
            "language, or a title search. Multiple identifiers for the "
            "same filter are combined with OR; thematic and entity "
            "filters are also combined with OR."
        ),
        parameters=[
            OpenApiParameter(
                name="thematic_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
                description=_("Thematic identifiers."),
            ),
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
                description=_("Entity identifiers."),
            ),
            OpenApiParameter(
                name="format_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
                description=_("Format identifiers."),
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
class NewsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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

        thematic_ids = _parse_id_list(self.request.query_params, "thematic_id")
        entity_ids = _parse_id_list(self.request.query_params, "entity_id")
        format_ids = _parse_id_list(self.request.query_params, "format_id")

        if thematic_ids is None or entity_ids is None or format_ids is None:
            translations_qs = translations_qs.none()
        else:
            filter_q = Q()
            if thematic_ids:
                filter_q |= Q(news__thematics__id__in=thematic_ids)
            if entity_ids:
                filter_q |= Q(news__entities__id__in=entity_ids)
            if filter_q:
                translations_qs = translations_qs.filter(filter_q)

            if format_ids:
                translations_qs = translations_qs.filter(
                    news__format__id__in=format_ids,
                )

        search = self.request.query_params.get("search")
        if search:
            translations_qs = translations_qs.filter(
                title__icontains=search.strip(),
            )

        return translations_qs.select_related("news").order_by("-published_at")
