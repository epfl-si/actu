from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.shortcuts import resolve_url
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


class HomepageUsersManageViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="cnoel",
            sciper="99999991",
            email="clement.noel@epfl.ch",
        )
        self.attached_user = User.objects.create_user(
            username="stawk",
            sciper="99999992",
            first_name="Samer",
            last_name="Tawk",
            email="samer.tawk@epfl.ch",
        )
        self.unattached_user = User.objects.create_user(
            username="ngreene",
            sciper="99999993",
            first_name="Nancy",
            last_name="Greene",
            email="nancy.greene@epfl.ch",
        )
        self.target_user = User.objects.create_user(
            username="eledecka",
            sciper="99999994",
            first_name="Ester",
            last_name="Ledecka",
            email="ester.ledecka@epfl.ch",
        )

        self.thematic = Thematic.objects.create()

        self.homepage = Homepage.objects.create(
            slug="test-homepage-slug", thematic=self.thematic
        )

        self.homepage.users.add(self.attached_user)
        self.homepage.users.add(self.target_user)

        self.url = reverse(
            "manage_homepage_users", kwargs={"pk": self.homepage.pk}
        )

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        login_url = resolve_url(settings.LOGIN_URL)
        self.assertTrue(login_url in response.url)

    def test_unauthorized_user_gets_403(self):
        self.client.force_login(self.unattached_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authorized_user_gets_200(self):
        self.client.force_login(self.attached_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["homepage"], self.homepage)
        self.assertIn(self.attached_user, response.context["current_users"])

    def test_admin_gets_200(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ajax_search_too_short(self):
        self.client.force_login(self.attached_user)
        response = self.client.get(
            self.url, {"q": "ab"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": []})

    @patch("homepages.views.AccredServiceClient")
    def test_ajax_search_valid(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.search_persons_by_right.return_value = [
            {
                "sciper": "99999992",
                "display_name": "Alexis Pinturault",
                "first_name": "Alexis",
                "last_name": "Pinturault",
            },
            {
                "sciper": "99999995",
                "display_name": "mhirscher",
                "first_name": "Marcel",
                "last_name": "Hirscher",
            },
        ]

        self.client.force_login(self.attached_user)
        response = self.client.get(
            self.url, {"q": "Dupont"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sciper"], "99999995")

    def test_post_add_no_sciper(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {"action": "add"}, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, "error")

    def test_post_add_existing_local_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"action": "add", "sciper": "99999993"}, follow=True
        )

        self.assertTrue(self.homepage.users.filter(sciper="99999993").exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].level_tag, "success")

    @patch("homepages.views.AccredServiceClient")
    def test_post_add_new_user_via_api(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.get_person_details.return_value = {
            "sciper": "99999996",
            "username": "lbianchi",
            "first_name": "Lara",
            "last_name": "Bianchi",
            "email": ".bianchi@epfl.ch",
        }

        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"action": "add", "sciper": "99999996"}, follow=True
        )

        new_user = User.objects.filter(sciper="99999996").first()
        self.assertIsNotNone(new_user)
        self.assertTrue(self.homepage.users.filter(id=new_user.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].level_tag, "success")

    @patch("homepages.views.AccredServiceClient")
    def test_post_add_api_not_found(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.get_person_details.return_value = None

        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"action": "add", "sciper": "99999999"}, follow=True
        )

        self.assertFalse(User.objects.filter(sciper="99999999").exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].level_tag, "error")

    def test_post_remove_user(self):
        self.client.force_login(self.admin)

        self.assertTrue(
            self.homepage.users.filter(id=self.target_user.id).exists()
        )

        response = self.client.post(
            self.url,
            {"action": "remove", "user_id": self.target_user.id},
            follow=True,
        )

        self.assertFalse(
            self.homepage.users.filter(id=self.target_user.id).exists()
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].level_tag, "success")

    def test_post_remove_invalid_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"action": "remove", "user_id": 9999}
        )
        self.assertEqual(response.status_code, 404)
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
