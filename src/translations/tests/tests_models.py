from django.contrib.auth import get_user_model
from django.test import TestCase

from news.models import News
from news_formats.models import NewsFormat
from translations.models import NewsTranslation

User = get_user_model()


class NewsTranslationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="iivo.niskanen",
            sciper="123456",
        )
        self.format, _ = NewsFormat.objects.get_or_create(
            id=1, defaults={"label_fr": "News de test"}
        )
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            title="Niskanen wins men's 50 km mass start classic",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_str(self):
        self.assertEqual(
            str(self.translation),
            "Niskanen wins men's 50 km mass start classic [en]",
        )

    def test_default_status_is_draft(self):
        self.assertEqual(self.translation.status, NewsTranslation.Status.DRAFT)

    def test_is_published_false_when_draft(self):
        self.assertFalse(self.translation.is_published)

    def test_is_published_true_when_published(self):
        self.translation.status = NewsTranslation.Status.PUBLISHED
        self.translation.save()
        self.assertTrue(self.translation.is_published)

    def test_unique_together_news_and_language(self):
        with self.assertRaises(Exception):
            NewsTranslation.objects.create(
                news=self.news,
                language="en",
                title="Duplicate translation",
                created_by=self.user,
            )

    def test_can_create_different_language_translation(self):
        NewsTranslation.objects.create(
            news=self.news,
            language="fr",
            title="Niskanen remporte le 50 km classique",
            created_by=self.user,
        )
        self.assertEqual(
            NewsTranslation.objects.filter(news=self.news).count(), 2
        )

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.translation.created_at)

    def test_created_by_is_set(self):
        self.assertEqual(self.translation.created_by, self.user)

    def test_updated_at_is_set(self):
        self.assertIsNotNone(self.translation.updated_at)

    def test_updated_by_is_none_by_default(self):
        self.assertIsNone(self.translation.updated_by)

    def test_published_at_is_none_by_default(self):
        self.assertIsNone(self.translation.published_at)

    def test_published_by_is_none_by_default(self):
        self.assertIsNone(self.translation.published_by)
