import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from media.models import NewsImage
from news.models import News
from news_formats.models import NewsFormat
from thematics.models import Thematic

User = get_user_model()


def _create_image_file(name="test.jpg"):
    from PIL import Image

    image = Image.new("RGB", (1600, 900), (255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


class NewsImageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.thematic = Thematic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news.thematics.add(self.thematic)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_str_returns_image_id_and_name(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            created_by=self.user,
        )
        self.assertEqual(
            str(news_image),
            f"Image #{news_image.pk} (news/images/{self.news.pk}/test.jpg)",
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_get_alt_text_with_language_fallback(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            alt_text_en="English alt",
            alt_text_fr="Texte alternatif",
            created_by=self.user,
        )
        self.assertEqual(news_image.get_alt_text("fr"), "Texte alternatif")
        self.assertEqual(news_image.get_alt_text("de"), "English alt")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_get_caption_with_language_fallback(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            caption_en="English caption",
            created_by=self.user,
        )
        self.assertEqual(news_image.get_caption("en"), "English caption")
        self.assertEqual(news_image.get_caption("it"), "English caption")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_created_by_is_set(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            created_by=self.user,
        )
        self.assertEqual(news_image.created_by, self.user)
