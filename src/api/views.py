from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.filters import ThematicFilter
from api.serializers import ThematicSerializer
from thematics.models import Thematic


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
