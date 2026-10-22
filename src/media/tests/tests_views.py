import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from media.models import NewsImage
from news.models import News
from news_formats.models import NewsFormat
from topics.models import Topic

from .utils import create_image_file

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class NewsImageEndpointsTest(TestCase):

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
        self.client.force_login(self.user)

        news_format = NewsFormat.objects.create(label_en="Article")
        topic = Topic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.user,
            format=news_format,
        )
        self.news.topics.add(topic)

    def upload_url(self, news_id=None):
        return reverse(
            "upload_news_images",
            kwargs={"news_id": news_id or self.news.pk},
        )

    def edit_url(self, image_id, news_id=None):
        return reverse(
            "edit_news_image",
            kwargs={"news_id": news_id or self.news.pk, "image_id": image_id},
        )

    def delete_url(self, image_id, news_id=None):
        return reverse(
            "delete_news_image",
            kwargs={"news_id": news_id or self.news.pk, "image_id": image_id},
        )

    # Upload

    def test_upload_multiple_images(self):
        response = self.client.post(
            self.upload_url(),
            {
                "images": [
                    create_image_file("one.jpg"),
                    create_image_file("two.png"),
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["errors"], [])
        self.assertEqual(len(data["images"]), 2)
        self.assertEqual(NewsImage.objects.filter(news=self.news).count(), 2)

        for image_data in data["images"]:
            stored = NewsImage.objects.get(pk=image_data["id"])
            self.assertTrue(os.path.exists(stored.image.path))
            self.assertEqual(stored.created_by, self.user)

    def test_upload_rejects_unsupported_format_and_rolls_back(self):
        response = self.client.post(
            self.upload_url(),
            {
                "images": [
                    create_image_file("valid.jpg"),
                    create_image_file("invalid.gif"),
                ],
            },
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["images"], [])
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("invalid.gif", data["errors"][0])
        self.assertFalse(NewsImage.objects.exists())

    def test_upload_rejects_undersized_image(self):
        response = self.client.post(
            self.upload_url(),
            {"images": [create_image_file("small.jpg", size=(800, 450))]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("1440", response.json()["errors"][0])
        self.assertFalse(NewsImage.objects.exists())

    def test_upload_rejects_corrupted_file(self):
        corrupted = SimpleUploadedFile(
            "corrupted.jpg",
            b"not-an-image",
            content_type="image/jpeg",
        )

        response = self.client.post(
            self.upload_url(),
            {"images": [corrupted]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("corrupted.jpg", response.json()["errors"][0])
        self.assertFalse(NewsImage.objects.exists())

    def test_upload_requires_a_file(self):
        response = self.client.post(self.upload_url(), {})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertFalse(NewsImage.objects.exists())

    def test_upload_rejects_get_requests(self):
        response = self.client.get(self.upload_url())

        self.assertEqual(response.status_code, 405)

    def test_upload_redirects_anonymous_user(self):
        self.client.logout()

        response = self.client.post(self.upload_url(), {})

        self.assertEqual(response.status_code, 302)

    def test_upload_returns_404_for_unknown_news(self):
        response = self.client.post(
            self.upload_url(news_id=self.news.pk + 1000),
            {"images": [create_image_file()]},
        )

        self.assertEqual(response.status_code, 404)

    # Edit

    def test_edit_news_image_metadata(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=create_image_file(),
            created_by=self.user,
        )

        response = self.client.post(
            self.edit_url(news_image.pk),
            {
                "alt_text_en": "Campus in autumn",
                "caption_fr": "Le campus en automne",
                "author": "Alain Ro",
                "rights": "EPFL",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(
            response.json()["image"]["alt_text_en"], "Campus in autumn"
        )

        news_image.refresh_from_db()
        self.assertEqual(news_image.alt_text_en, "Campus in autumn")
        self.assertEqual(news_image.caption_fr, "Le campus en automne")
        self.assertEqual(news_image.author, "Alain Ro")
        self.assertEqual(news_image.rights, "EPFL")

    def test_edit_rejects_too_long_metadata(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=create_image_file(),
            created_by=self.user,
        )

        response = self.client.post(
            self.edit_url(news_image.pk),
            {"alt_text_en": "x" * 201},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_edit_returns_404_for_image_of_another_news(self):
        other_news = News.objects.create(
            created_by=self.user,
            format=self.news.format,
        )
        news_image = NewsImage.objects.create(
            news=other_news,
            image=create_image_file(),
            created_by=self.user,
        )

        response = self.client.post(self.edit_url(news_image.pk), {})

        self.assertEqual(response.status_code, 404)

    # Delete

    def test_delete_news_image_removes_row_and_file(self):
        news_image = NewsImage.objects.create(
            news=self.news,
            image=create_image_file("delete-me.jpg"),
            created_by=self.user,
        )
        file_path = news_image.image.path

        response = self.client.post(self.delete_url(news_image.pk))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(NewsImage.objects.exists())
        self.assertFalse(os.path.exists(file_path))

    def test_delete_returns_404_for_unknown_image(self):
        response = self.client.post(self.delete_url(99999))

        self.assertEqual(response.status_code, 404)
