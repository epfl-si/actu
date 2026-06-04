from django.contrib import admin

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields = Entity.search_fields

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
        if not obj.is_main:
            obj.order = 0
            super().save_model(request, obj, form, change)
            self.reorder_everything()
            return

        existing_entities = list(
            Entity.objects.filter(order__gt=0)
            .exclude(pk=obj.pk)
            .order_by("order")
        )

        max_possible_order = len(existing_entities) + 1

        if obj.order <= 0 or obj.order > max_possible_order:
            obj.order = max_possible_order

        target_index = max(0, obj.order - 1)
        existing_entities.insert(target_index, obj)

        for index, entity in enumerate(existing_entities, start=1):
            if entity.pk == obj.pk:
                obj.order = index
            else:
                if entity.order != index:
                    Entity.objects.filter(pk=entity.pk).update(order=index)

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.reorder_everything()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        self.reorder_everything()

    def reorder_everything(self):
        all_ordered_entities = Entity.objects.filter(order__gt=0).order_by(
            "order"
        )
        for index, entity in enumerate(all_ordered_entities, start=1):
            if entity.order != index:
                Entity.objects.filter(pk=entity.pk).update(order=index)
