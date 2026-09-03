import django_filters
from django.db import models
from django.utils.translation import gettext_lazy as _

from entities.models import Entity
from thematics.models import Thematic


class LabelModelFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method="filter_search",
        help_text=_("Search across labels in all supported languages."),
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("order", "order"),
            ("label_de", "label_de"),
            ("label_en", "label_en"),
            ("label_fr", "label_fr"),
            ("label_it", "label_it"),
        ),
        help_text=_("Sort the results by the selected field."),
    )

    class Meta:
        fields = []

    def filter_search(self, queryset, _name, value):
        value = value.strip()
        if not value:
            return queryset
        q = models.Q()
        for field in self._meta.model.search_fields:
            q |= models.Q(**{f"{field}__icontains": value})
        return queryset.filter(q)


class EntityFilter(LabelModelFilter):
    is_main = django_filters.BooleanFilter(
        help_text=_("Filter by whether the entity is marked as main."),
    )

    class Meta(LabelModelFilter.Meta):
        model = Entity


class ThematicFilter(LabelModelFilter):
    is_main = django_filters.BooleanFilter(
        help_text=_("Filter by whether the thematic is marked as main."),
    )

    class Meta(LabelModelFilter.Meta):
        model = Thematic
