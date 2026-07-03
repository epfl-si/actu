from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from homepages.models import Homepage, HomepageTranslation
from thematics.models import Thematic

User = get_user_model()


class HomepagesViewsTests(TestCase):

    def test_title_homepage_fr(self):
        with translation.override("fr"):
            response = self.client.get(reverse("homepages"))
            self.assertEqual(200, response.status_code)
            self.assertIn(
                "<title>Actualités - EPFL</title>",
                response.content.decode(),
            )


class CreateHomepageTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="niskanen",
            sciper="123456",
        )
        self.other_user = User.objects.create_user(
            username="odermatt",
            sciper="654321",
        )
        self.thematic = Thematic.objects.create(
            label_en="AI",
            label_fr="IA",
        )
        self.homepage = Homepage.objects.create(
            slug="ai",
            thematic=self.thematic,
        )
        self.homepage.users.add(self.user)

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_creates_translation_successfully(self):
        self.client.force_login(self.user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            HomepageTranslation.objects.filter(
                homepage=self.homepage, language="en"
            ).exists()
        )
        translation_obj = HomepageTranslation.objects.get(
            homepage=self.homepage, language="en"
        )
        self.assertEqual(translation_obj.created_by, self.user)
        self.assertEqual(
            translation_obj.status, HomepageTranslation.Status.DRAFT
        )

    def test_user_without_permission_gets_404(self):
        self.client.force_login(self.other_user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_language_shows_error_message(self):
        self.client.force_login(self.user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "fi"],
        )
        response = self.client.get(url, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid language", str(messages[0]))

    def test_existing_translation_shows_warning_message(self):
        HomepageTranslation.objects.create(
            homepage=self.homepage,
            language="en",
            created_by=self.user,
        )
        self.client.force_login(self.user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.get(url, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("already exists", str(messages[0]))
        self.assertEqual(
            HomepageTranslation.objects.filter(
                homepage=self.homepage, language="en"
            ).count(),
            1,
        )
