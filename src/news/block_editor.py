"""Shared definition of the news page content blocks.

The block type keys are persisted in ``NewsTranslation.content``; the labels
are translatable and handed to the block editor React island as props.
"""

from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

BLOCK_TYPES = {
    "text": _("Text"),
}

BLOCK_FIELD_LABELS = {
    "content": _("Text"),
}

BLOCK_EDITOR_LABELS = {
    "addBlock": _("Add a block"),
    "moveUp": _("Move the block up"),
    "moveDown": _("Move the block down"),
    "edit": _("Edit the block"),
    "remove": _("Delete the block"),
    "reorder": _("Reorder the block"),
    "save": _("Save"),
    "cancel": _("Cancel"),
    # JS-side interpolation of the block type label.
    "editBlockTitle": _("Edit the {type} block"),
}


def news_blocks_editor_props(news, lang, translation):
    """Build the props of the news blocks editor React island."""
    return {
        "newsId": news.pk if news else None,
        "language": lang,
        # UI language the user picked on the site, for editor (TinyMCE).
        "uiLanguage": get_language(),
        "blocks": translation.content if translation else [],
        "i18n": {
            **{key: str(label) for key, label in BLOCK_EDITOR_LABELS.items()},
            "blockTypes": {
                key: str(label) for key, label in BLOCK_TYPES.items()
            },
            "fieldLabels": {
                key: str(label) for key, label in BLOCK_FIELD_LABELS.items()
            },
        },
    }
