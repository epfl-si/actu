import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from media.models import NewsImage
from news.models import News
from news_formats.models import NewsFormat
from topics.models import Topic

User = get_user_model()


def _create_image_file(name="test.jpg"):
    from PIL import Image

    image = Image.new("RGB", (1600, 900), (255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class NewsImagesAPITests(TestCase):

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
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news.topics.add(self.topic)

    def test_list_images_for_news(self):
        NewsImage.objects.create(
            news=self.news,
            image=_create_image_file("first.jpg"),
            created_by=self.user,
            alt_text_en="First alt",
        )
        NewsImage.objects.create(
            news=self.news,
            image=_create_image_file("second.jpg"),
            created_by=self.user,
            caption_en="Second caption",
        )

        url = reverse(
            "news-images", kwargs={"version": "v1", "news_pk": self.news.pk}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

        image_names = [item["image"] for item in response.json()]
        self.assertTrue(
            all(
                name.startswith("http://testserver/uploads/news/images/")
                for name in image_names
            )
        )

    def test_list_images_is_empty_for_news_without_images(self):
        url = reverse(
            "news-images", kwargs={"version": "v1", "news_pk": self.news.pk}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_list_images_returns_404_for_unknown_news(self):
        url = reverse(
            "news-images", kwargs={"version": "v1", "news_pk": 99999}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_images_requires_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse(
            "news-images", kwargs={"version": "v1", "news_pk": self.news.pk}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_files_are_cleaned_up_after_tests(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=_create_image_file("cleanup.jpg"),
            created_by=self.user,
        )
        self.assertTrue(os.path.exists(news_image.image.path))
