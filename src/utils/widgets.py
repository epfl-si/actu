from django.forms import Media
from django.utils.functional import cached_property
from django_editorjs_fields import EditorJsWidget


class EditorJsExtendedWidget(EditorJsWidget):
    """Editor.js widget enriched with some plugins:
    - drag-and-drop block reordering
    """

    DRAG_DROP_VERSION = "1.1.16"

    @cached_property
    def media(self):
        parent_media = super().media
        js = list(parent_media._js)

        init_index = js.index(
            "django-editorjs-fields/js/django-editorjs-fields.js"
        )
        drag_drop_url = "//cdn.jsdelivr.net/npm/editorjs-drag-drop@{}".format(
            self.DRAG_DROP_VERSION
        )
        js.insert(init_index, drag_drop_url)
        js.insert(init_index, "editorjs/js/editorjs-init.js")

        return Media(js=js, css=parent_media._css)
