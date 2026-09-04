from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from api.views import NewsViewSet, \
    EntityViewSet, ThematicViewSet

router = DefaultRouter()
router.register(r"entities", EntityViewSet, basename="entity")
router.register(r"thematics", ThematicViewSet, basename="thematic")
router.register(r"news", NewsViewSet, basename="news")


urlpatterns = [
    path(
        "schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[AllowAny]
        ),
        name="api-docs",
    ),
    path("", include(router.urls)),
]
