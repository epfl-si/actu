import os
import shutil
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

    def test_get_caption_with_language_fallback(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            caption_en="English caption",
            created_by=self.user,
        )
        self.assertEqual(news_image.get_caption("en"), "English caption")
        self.assertEqual(news_image.get_caption("it"), "English caption")

    def test_created_by_is_set(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            created_by=self.user,
        )
        self.assertEqual(news_image.created_by, self.user)

    def test_image_file_is_deleted_on_news_image_delete(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file(),
            created_by=self.user,
        )
        file_path = news_image.image.path
        self.assertTrue(os.path.exists(file_path))

        news_image.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_old_image_file_is_deleted_on_image_replace(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file("original.jpg"),
            created_by=self.user,
        )
        old_file_path = news_image.image.path
        self.assertTrue(os.path.exists(old_file_path))

        news_image.image = _create_image_file("replacement.jpg")
        news_image.save()

        self.assertFalse(os.path.exists(old_file_path))
        self.assertTrue(os.path.exists(news_image.image.path))
