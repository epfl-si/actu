from django.utils.translation import gettext_lazy as _

from utils.models import LabelModel


class BlockType(LabelModel):
    class Meta:
        db_table = "block_types"
        verbose_name = _("Block Type")
        verbose_name_plural = _("Block Types")
