class ImageResolutionConverter:
    """Match an image serving resolution: "original" or "WxH" in pixels."""

    regex = "original|[1-9][0-9]{0,3}x[1-9][0-9]{0,3}"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)
