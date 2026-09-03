from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import localtime, now

from news.models import News
from news_formats.models import NewsFormat
from translations.models import NewsSlugHistory, NewsTranslation

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

    def test_last_activity_label_for_draft_without_update(self):
        label = self.translation.last_activity_label
        expected_date = localtime(self.translation.created_at).strftime(
            "%d.%m.%Y %H:%M"
        )
        self.assertIn("Created", label)
        self.assertIn(expected_date, label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)

    def test_last_activity_label_for_draft_with_update(self):
        other_user = User.objects.create(
            username="niskanen",
            sciper="88888888",
            first_name="Iivo",
            last_name="Niskanen",
        )
        self.translation.updated_by = other_user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Updated", label)
        self.assertIn("Iivo Niskanen", label)

    def test_last_activity_label_for_published(self):
        self.translation.status = NewsTranslation.Status.PUBLISHED
        self.translation.published_at = now()
        self.translation.published_by = self.user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Published", label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)

    def test_last_activity_label_for_archived(self):
        self.translation.status = NewsTranslation.Status.ARCHIVED
        self.translation.updated_by = self.user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Archived", label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)

    def test_slug_history_not_created_on_initial_save(self):
        self.assertEqual(NewsSlugHistory.objects.count(), 0)

    def test_slug_history_created_on_slug_change(self):
        original_slug = self.translation.slug

        self.translation.title = "A completely new title"
        self.translation.save()

        new_slug = self.translation.slug

        self.assertNotEqual(original_slug, new_slug)

        self.assertTrue(
            NewsSlugHistory.objects.filter(
                news_translation=self.translation, old_slug=original_slug
            ).exists()
        )

    def test_slug_history_anti_loop_on_revert(self):
        original_title = self.translation.title
        original_slug = self.translation.slug

        self.translation.title = "Second title"
        self.translation.save()
        second_slug = self.translation.slug

        self.assertTrue(
            NewsSlugHistory.objects.filter(
                news_translation=self.translation, old_slug=original_slug
            ).exists()
        )

        self.translation.title = original_title
        self.translation.save()

        self.assertEqual(self.translation.slug, original_slug)

        self.assertFalse(
            NewsSlugHistory.objects.filter(
                news_translation=self.translation, old_slug=original_slug
            ).exists()
        )

        self.assertTrue(
            NewsSlugHistory.objects.filter(
                news_translation=self.translation, old_slug=second_slug
            ).exists()
        )
