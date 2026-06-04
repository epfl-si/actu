from django.contrib import admin

from .models import Thematic


@admin.register(Thematic)
class ThematicAdmin(admin.ModelAdmin):
    search_fields = Thematic.search_fields

    list_display = (
        "label_en",
        "is_active",
        "is_main",
        "has_homepage",
        "order",
    )

    ordering = ("-is_main", "order", "label_en")

    list_filter = (
        "is_active",
        "is_main",
        "has_homepage",
    )

    def save_model(self, request, obj, form, change):
        existing_entities = list(
            Thematic.objects.filter(order__gt=0)
            .exclude(pk=obj.pk)
            .order_by("order")
        )

        max_possible_order = len(existing_entities) + 1

        if obj.order <= 0 or obj.order > max_possible_order:
            obj.order = max_possible_order

        target_index = max(0, obj.order - 1)
        existing_entities.insert(target_index, obj)

        for index, thematic in enumerate(existing_entities, start=1):
            if thematic.pk == obj.pk:
                obj.order = index
            else:
                if thematic.order != index:
                    Thematic.objects.filter(pk=thematic.pk).update(order=index)

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.reorder_everything()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        self.reorder_everything()

    def reorder_everything(self):
        all_ordered_entities = Thematic.objects.filter(order__gt=0).order_by(
            "order"
        )
        for index, thematic in enumerate(all_ordered_entities, start=1):
            if thematic.order != index:
                Thematic.objects.filter(pk=thematic.pk).update(order=index)
