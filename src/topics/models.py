from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.models import AuditModelMixin
from utils.models import LabelModel


class Topic(AuditModelMixin, LabelModel):
    """
    A topic that news can be related to.

    For example : AI, Health, Energy, ...
    """

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether this topic is active and visible in "
            "the system."
        ),
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main"),
        help_text=_(
            "Designates whether this topic is displayed on the main menu."
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
            Topic.reorder_everything()
            return

        existing_topics = list(
            Topic.objects.filter(order__gt=0)
            .exclude(pk=self.pk)
            .order_by("order")
        )

        max_possible_order = len(existing_topics) + 1
        if self.order <= 0 or self.order > max_possible_order:
            self.order = max_possible_order

        target_index = max(0, self.order - 1)
        existing_topics.insert(target_index, self)

        to_update = []
        for index, topic in enumerate(existing_topics, start=1):
            if topic.pk == self.pk:
                self.order = index
            else:
                if topic.order != index:
                    topic.order = index
                    to_update.append(topic)

        if to_update:
            Topic.objects.bulk_update(to_update, ["order"])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Topic.reorder_everything()

    @classmethod
    def reorder_everything(cls):
        all_ordered = cls.objects.filter(order__gt=0).order_by("order")
        to_update = []
        for index, topic in enumerate(all_ordered, start=1):
            if topic.order != index:
                topic.order = index
                to_update.append(topic)

        if to_update:
            cls.objects.bulk_update(to_update, ["order"])
