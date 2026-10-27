from django.conf import settings


class ImageResolutionConverter:
    """Match an image serving resolution: "original" or "WxH" in pixels."""

    regex = r"original|[1-9][0-9]{0,3}x[1-9][0-9]{0,3}"

    def to_python(self, value):
        if value == "original":
            return value

        width, height = map(int, value.split("x"))
        _ensure_within_pixel_limit(width, height)
        return width, height

    def to_url(self, value):
        if value == "original":
            return value

        width, height = value
        _ensure_within_pixel_limit(width, height)
        return f"{width}x{height}"


def _ensure_within_pixel_limit(width, height):
    """Raise ValueError above MAX_IMAGE_PIXELS_SERVING (ValueError -> 404)."""
    if width * height > settings.MAX_IMAGE_PIXELS_SERVING:
        raise ValueError("Image dimensions exceed the maximum pixel count")
