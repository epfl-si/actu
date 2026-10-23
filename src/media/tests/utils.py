from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

IMAGE_FORMAT_BY_EXTENSION = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
}


def create_image_file(name="test.jpg", size=(1600, 900), color=(255, 0, 0)):
    """Build an in-memory image upload whose format matches its extension."""
    extension = name.rsplit(".", 1)[-1].lower()
    image_format = IMAGE_FORMAT_BY_EXTENSION.get(extension)
    if image_format is None:
        raise ValueError(f"Unsupported test image extension: {name}")

    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    buffer.seek(0)
    content_type = (
        "image/jpeg" if image_format == "JPEG" else f"image/{extension}"
    )
    return SimpleUploadedFile(name, buffer.read(), content_type=content_type)
