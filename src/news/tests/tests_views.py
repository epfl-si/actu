from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import News
from translations.models import NewsTranslation

User = get_user_model()


class ManageNewsViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )

    def test_limits_to_ten_news_per_page(self):
        for index in range(12):
            news = News.objects.create(created_by=self.user)
            NewsTranslation.objects.create(
                news=news,
                language="en",
                status=NewsTranslation.Status.DRAFT,
                created_by=self.user,
            )

        self.client.force_login(self.user)
        response = self.client.get(reverse("manage_news"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["news_rows"]), 10)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertTrue(response.context["page_obj"].has_next())


class DeleteNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.news = News.objects.create(created_by=self.user)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_archives_translation_successfully(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            NewsTranslation.Status.ARCHIVED,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_already_archived_shows_warning(self):
        self.translation.status = NewsTranslation.Status.ARCHIVED
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("already archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("archived successfully", str(messages[0]))


class RestoreNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.news = News.objects.create(created_by=self.user)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            status=NewsTranslation.Status.ARCHIVED,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_restores_translation_to_draft(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            NewsTranslation.Status.DRAFT,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_not_archived_shows_warning(self):
        self.translation.status = NewsTranslation.Status.DRAFT
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("not archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("restored successfully", str(messages[0]))
