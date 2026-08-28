from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin
from utils.models import LabelModel


class Thematic(AuditModelMixin, LabelModel):
    """
    Thematic is a topic

    For example : AI, Health, Energy, ...
    """

    class Meta:
        verbose_name = _("Thematic")
        verbose_name_plural = _("Thematics")

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether this thematic is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main"),
        help_text=_(
            "Designates whether this thematic is displayed on the main menu."
        ),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Defines the display order."),
    )

    def save(self, *args, **kwargs):
        if not self.is_active or not self.is_main:
            self.order = 0
            super().save(*args, **kwargs)
            Thematic.reorder_everything()
            return

        existing_thematics = list(
            Thematic.objects.filter(order__gt=0)
            .exclude(pk=self.pk)
            .order_by("order")
        )

        max_possible_order = len(existing_thematics) + 1
        if self.order <= 0 or self.order > max_possible_order:
            self.order = max_possible_order

        target_index = max(0, self.order - 1)
        existing_thematics.insert(target_index, self)

        to_update = []
        for index, thematic in enumerate(existing_thematics, start=1):
            if thematic.pk == self.pk:
                self.order = index
            else:
                if thematic.order != index:
                    thematic.order = index
                    to_update.append(thematic)

        if to_update:
            Thematic.objects.bulk_update(to_update, ["order"])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Thematic.reorder_everything()

    @classmethod
    def reorder_everything(cls):
        all_ordered = cls.objects.filter(order__gt=0).order_by("order")
        to_update = []
        for index, thematic in enumerate(all_ordered, start=1):
            if thematic.order != index:
                thematic.order = index
                to_update.append(thematic)

        if to_update:
            cls.objects.bulk_update(to_update, ["order"])
