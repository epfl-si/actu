import PIL.Image
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import NewsImage

MIN_IMAGE_WIDTH = 1440
MIN_IMAGE_HEIGHT = 810
ALLOWED_IMAGE_FORMATS = ("JPEG", "PNG")


class MultipleFileInput(forms.ClearableFileInput):
    """File input accepting several selected files at once."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """FileField returning a list of cleaned files instead of a single one."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            if not data:
                # An empty list means no file was submitted: let the
                # required validation apply instead of skipping it.
                data = None
            else:
                return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


def _validate_image_file(image):
    """Return an error message if the file is not a usable news image."""
    name = getattr(image, "name", "")
    try:
        image.seek(0)
        with PIL.Image.open(image) as probe:
            probe.verify()

        image.seek(0)
        with PIL.Image.open(image) as probe:
            if probe.format not in ALLOWED_IMAGE_FORMATS:
                return _(
                    "'%(name)s': only JPEG and PNG images are accepted."
                ) % {"name": name}
            if (
                probe.width < MIN_IMAGE_WIDTH
                or probe.height < MIN_IMAGE_HEIGHT
            ):
                return _(
                    "'%(name)s': the image must be at least "
                    "%(width)d x %(height)d pixels."
                ) % {
                    "name": name,
                    "width": MIN_IMAGE_WIDTH,
                    "height": MIN_IMAGE_HEIGHT,
                }
    except (OSError, ValueError, PIL.Image.DecompressionBombError):
        return _("'%(name)s': this file is not a valid image.") % {
            "name": name
        }
    return None


class NewsImageForm(forms.ModelForm):
    """Edit the metadata of an existing news image."""

    class Meta:
        model = NewsImage
        fields = [
            "alt_text_fr",
            "alt_text_en",
            "alt_text_de",
            "alt_text_it",
            "caption_fr",
            "caption_en",
            "caption_de",
            "caption_it",
            "author",
            "rights",
        ]


class MultipleImageUploadForm(forms.Form):
    """Upload one or more images at once for a news item."""

    images = MultipleFileField(label=_("Images"))

    def clean_images(self):
        images = self.cleaned_data.get("images")
        if not isinstance(images, (list, tuple)):
            images = [images]

        errors = []
        for image in images:
            error = _validate_image_file(image)
            if error:
                errors.append(error)

        # All-or-nothing: a single bad file rejects the whole upload.
        if errors:
            raise forms.ValidationError(errors)

        return images
