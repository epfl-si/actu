from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import LabelModel


class Entity(LabelModel):
    """
    Entity is a first-level LDAP group at EPFL

    For example : SV, SB, ENAC, ...
    """

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether this entity is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main"),
        help_text=_(
            "Designates whether this entity (School) is displayed on the "
            "footer."
        ),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_(
            "Defines the display order. A value of 0 means that the order "
            "is ignored (for non-main entities)."
        ),
    )

    def save(self, *args, **kwargs):
        if not self.is_active or not self.is_main:
            self.order = 0
            super().save(*args, **kwargs)
            Entity.reorder_everything()
            return

        existing_entities = list(
            Entity.objects.filter(order__gt=0)
            .exclude(pk=self.pk)
            .order_by("order")
        )

        max_possible_order = len(existing_entities) + 1
        if self.order <= 0 or self.order > max_possible_order:
            self.order = max_possible_order

        target_index = max(0, self.order - 1)
        existing_entities.insert(target_index, self)

        to_update = []
        for index, entity in enumerate(existing_entities, start=1):
            if entity.pk == self.pk:
                self.order = index
            else:
                if entity.order != index:
                    entity.order = index
                    to_update.append(entity)

        if to_update:
            Entity.objects.bulk_update(to_update, ["order"])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Entity.reorder_everything()

    @classmethod
    def reorder_everything(cls):
        """Parcourt la table et réindexe proprement via bulk_update"""
        all_ordered = cls.objects.filter(order__gt=0).order_by("order")
        to_update = []
        for index, entity in enumerate(all_ordered, start=1):
            if entity.order != index:
                entity.order = index
                to_update.append(entity)

        if to_update:
            cls.objects.bulk_update(to_update, ["order"])
