from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import News
from news_formats.models import NewsFormat
from topics.models import Topic
from translations.models import NewsTranslation

User = get_user_model()


class NewsAdminTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="lovelace",
            password="99999999",
            is_staff=True,
            is_superuser=True,
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.admin_user,
            format=self.format,
        )
        self.news.topics.add(self.topic)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            title="A title",
            created_by=self.admin_user,
        )

    def test_news_change_page_lists_translations_with_links(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("admin:news_news_change", args=[self.news.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A title [en] — Draft")
        self.assertContains(
            response,
            reverse(
                "admin:translations_newstranslation_change",
                args=[self.translation.pk],
            ),
        )

    def test_translations_overview_is_sorted_by_language(self):
        fr_translation = NewsTranslation.objects.create(
            news=self.news,
            language="fr",
            title="Un titre",
            created_by=self.admin_user,
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("admin:news_news_change", args=[self.news.pk])
        )

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertLess(
            html.index(
                reverse(
                    "admin:translations_newstranslation_change",
                    args=[self.translation.pk],
                )
            ),
            html.index(
                reverse(
                    "admin:translations_newstranslation_change",
                    args=[fr_translation.pk],
                )
            ),
        )

    def test_translations_overview_is_empty_without_translations(self):
        self.translation.delete()

        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("admin:news_news_change", args=[self.news.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "A title [en] — Draft")

    def test_translation_list_links_back_to_news(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("admin:translations_newstranslation_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("admin:news_news_change", args=[self.news.pk])
        )

    def test_translation_statuses_column(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:news_news_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "en: Draft")
        self.assertContains(response, "fr: —")
