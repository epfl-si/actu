from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import EntityFilter, TopicFilter
from api.pagination import NewsPagination
from api.serializers import (
    EntitySerializer,
    NewsImageSerializer,
    NewsSerializer,
    TopicSerializer,
)
from entities.models import Entity
from news.models import News
from topics.models import Topic
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


@extend_schema(tags=[_("Topics")])
@extend_schema_view(
    list=extend_schema(
        summary=_("List active topics"),
        description=_("Return all active topics ordered by identifier."),
    ),
    retrieve=extend_schema(
        summary=_("Retrieve a topic"),
        description=_("Return a single active topic by its identifier."),
    ),
)
class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.filter(is_active=True).order_by("id")
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]
    filterset_class = TopicFilter


@extend_schema(tags=[_("News")])
@extend_schema_view(
    list=extend_schema(
        summary=_("List published news"),
        description=_(
            "Return published news, optionally filtered by topic "
            "identifiers, entity identifiers, format identifiers, a "
            "language, or a title search. Multiple identifiers for the "
            "same filter are combined with OR; topic and entity "
            "filters are also combined with OR."
        ),
        parameters=[
            OpenApiParameter(
                name="topic_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
                description=_("Topic identifiers."),
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

        topic_ids = _parse_id_list(self.request.query_params, "topic_id")
        entity_ids = _parse_id_list(self.request.query_params, "entity_id")
        format_ids = _parse_id_list(self.request.query_params, "format_id")

        if topic_ids is None or entity_ids is None or format_ids is None:
            translations_qs = translations_qs.none()
        else:
            filter_q = Q()
            if topic_ids:
                filter_q |= Q(news__topics__id__in=topic_ids)
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


@extend_schema(
    tags=[_("News")],
    summary=_("List images for a news item"),
    description=_("Return all images attached to a given news item."),
    responses={200: NewsImageSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def news_images(request, version, news_pk):
    """Return the list of images for the requested news item."""
    news = get_object_or_404(News, pk=news_pk)
    serializer = NewsImageSerializer(
        news.images.all(),
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)
