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
            sciper="99999999",
        )
        self.other_user = User.objects.create_user(
            username="odermatt",
            sciper="88888888",
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
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_creates_translation_successfully(self):
        self.client.force_login(self.user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
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
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_language_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "create_homepage_translation",
            args=[self.homepage.id, "fi"],
        )
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)

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
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("already exists", str(messages[0]))
        self.assertEqual(
            HomepageTranslation.objects.filter(
                homepage=self.homepage, language="en"
            ).count(),
            1,
        )


class DeleteHomepageTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="niskanen",
            sciper="99999999",
        )
        self.other_user = User.objects.create_user(
            username="odermatt",
            sciper="88888888",
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
        self.translation = HomepageTranslation.objects.create(
            homepage=self.homepage,
            language="en",
            status=HomepageTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_archives_translation_successfully(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            HomepageTranslation.Status.ARCHIVED,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_user_without_permission_gets_404(self):
        self.client.force_login(self.other_user)
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_already_archived_shows_warning(self):
        self.translation.status = HomepageTranslation.Status.ARCHIVED
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("already archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("archived successfully", str(messages[0]))


class RestoreHomepageTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="niskanen",
            sciper="99999999",
        )
        self.other_user = User.objects.create_user(
            username="odermatt",
            sciper="88888888",
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
        self.translation = HomepageTranslation.objects.create(
            homepage=self.homepage,
            language="en",
            status=HomepageTranslation.Status.ARCHIVED,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_restores_translation_to_draft(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            HomepageTranslation.Status.DRAFT,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_user_without_permission_gets_404(self):
        self.client.force_login(self.other_user)
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_not_archived_shows_warning(self):
        self.translation.status = HomepageTranslation.Status.DRAFT
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("not archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_homepage_translation",
            args=[self.homepage.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("restored successfully", str(messages[0]))
