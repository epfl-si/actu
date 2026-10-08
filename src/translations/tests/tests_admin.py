from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import News
from news_formats.models import NewsFormat
from translations.models import NewsTranslation

User = get_user_model()


class NewsTranslationAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="iivo.niskanen",
            sciper="123456",
            is_staff=True,
            is_superuser=True,
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
        self.client.force_login(self.user)
        self.url = reverse(
            "admin:translations_newstranslation_change",
            args=[self.translation.pk],
        )

    def test_change_form_links_to_site_edit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "edit_news", args=[self.news.pk, self.translation.language]
            ),
        )

    def test_change_form_shows_edit_on_the_site_button(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Edit on the site")

    def test_change_form_replaces_view_on_site(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "View on site")

    def test_change_form_keeps_history_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, "historylink")
