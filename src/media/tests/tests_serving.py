import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from media.models import NewsImage
from news.models import News
from news_formats.models import NewsFormat

from .utils import create_image_file

User = get_user_model()


def open_response_image(response):
    """Reopen the JPEG bytes of a serving response."""
    return Image.open(BytesIO(response.content))


class ServeNewsImageTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._settings_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._settings_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._settings_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def setUp(self):
        user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        news_format = NewsFormat.objects.create(label_en="Article")
        self.news = News.objects.create(
            created_by=user,
            format=news_format,
        )

    def create_image(self, name="test.jpg", size=(1600, 900), **kwargs):
        return NewsImage.objects.create(
            news=self.news,
            image=create_image_file(name, size=size),
            created_by=self.news.created_by,
            **kwargs,
        )

    def serve_url(self, image_id, resolution):
        """Build the serving URL; WxH strings become (width, height)."""
        if resolution == "full":
            value = resolution
        else:
            value = tuple(map(int, resolution.split("x")))
        return reverse(
            "serve_news_image",
            kwargs={"image_id": image_id, "resolution": value},
        )

    def test_full_returns_source_dimensions(self):
        news_image = self.create_image()

        response = self.client.get(self.serve_url(news_image.pk, "full"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(response["Cache-Control"], "max-age=900, public")
        self.assertEqual(open_response_image(response).size, (1600, 900))

    def test_resolution_fits_within_box(self):
        news_image = self.create_image()

        response = self.client.get(self.serve_url(news_image.pk, "1440x810"))

        self.assertEqual(open_response_image(response).size, (1440, 810))

    def test_resolution_never_upscales(self):
        news_image = self.create_image(size=(800, 450))

        response = self.client.get(self.serve_url(news_image.pk, "1440x810"))

        self.assertEqual(open_response_image(response).size, (800, 450))

    def test_resolution_preserves_aspect_ratio(self):
        news_image = self.create_image(size=(2000, 1000))

        response = self.client.get(self.serve_url(news_image.pk, "800x600"))

        # 2000x1000 fitted within an 800x600 box keeps the 2:1 ratio.
        self.assertEqual(open_response_image(response).size, (800, 400))

    def test_crop_is_applied(self):
        news_image = self.create_image(
            crop_left=0,
            crop_upper=0,
            crop_right=1440,
            crop_lower=810,
        )

        response = self.client.get(self.serve_url(news_image.pk, "1440x810"))

        self.assertEqual(open_response_image(response).size, (1440, 810))

    def test_full_skips_crop(self):
        news_image = self.create_image(
            crop_left=0,
            crop_upper=0,
            crop_right=1440,
            crop_lower=810,
        )

        response = self.client.get(self.serve_url(news_image.pk, "full"))

        self.assertEqual(open_response_image(response).size, (1600, 900))

    def test_png_is_served_as_jpeg(self):
        news_image = self.create_image(name="test.png")

        response = self.client.get(self.serve_url(news_image.pk, "full"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(open_response_image(response).format, "JPEG")

    def test_transparency_is_flattened_on_white(self):
        buffer = BytesIO()
        Image.new("RGBA", (1600, 900), (255, 0, 0, 0)).save(
            buffer, format="PNG"
        )
        buffer.seek(0)
        news_image = NewsImage.objects.create(
            news=self.news,
            image=SimpleUploadedFile(
                "transparent.png", buffer.read(), content_type="image/png"
            ),
            created_by=self.news.created_by,
        )

        response = self.client.get(self.serve_url(news_image.pk, "full"))

        self.assertEqual(
            open_response_image(response).getpixel((0, 0)), (255, 255, 255)
        )

    def test_unknown_image_returns_404(self):
        response = self.client.get(self.serve_url(99999, "full"))

        self.assertEqual(response.status_code, 404)

    def test_invalid_resolution_returns_404(self):
        news_image = self.create_image()

        for resolution in ("zero", "0x100", "99999x100", "100x0", "x100"):
            response = self.client.get(
                f"/image/{news_image.pk}/{resolution}.jpg"
            )
            self.assertEqual(response.status_code, 404, resolution)

    def test_resolution_exceeding_pixel_limit_returns_404(self):
        news_image = self.create_image()

        # 9999x9999 passes the regex but exceeds MAX_IMAGE_PIXELS_SERVING.
        response = self.client.get(f"/image/{news_image.pk}/9999x9999.jpg")

        self.assertEqual(response.status_code, 404)

    def test_missing_file_returns_404(self):
        news_image = self.create_image()
        os.remove(news_image.image.path)

        response = self.client.get(self.serve_url(news_image.pk, "full"))

        self.assertEqual(response.status_code, 404)
