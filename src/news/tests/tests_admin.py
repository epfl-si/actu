from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import News
from news_formats.models import NewsFormat

User = get_user_model()


class NewsAdminTest(TestCase):
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
        self.client.force_login(self.user)
        self.url = reverse("admin:news_news_change", args=[self.news.pk])

    def test_change_form_links_to_site_edit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("edit_news", args=[self.news.pk, "en"]),
        )

    def test_change_form_shows_edit_on_the_site_button(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Edit on the site")

    def test_change_form_keeps_history_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, "historylink")
