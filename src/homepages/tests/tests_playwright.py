from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect

from homepages.models import Homepage, HomepageTranslation
from thematics.models import Thematic
from utils.testing import PlaywrightTestCase

User = get_user_model()


class ManageHomepagesPlaywrightTests(PlaywrightTestCase):

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(
            username="niskanen",
            sciper="99999999",
        )
        self.login_as(self.user)

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

    def test_delete_modal_shows_correct_homepage_and_lang(self):
        self.page.goto(self.live_server_url + reverse("manage_homepages"))

        self.page.click(
            'button[title="Delete"][data-homepage="AI"][data-lang="English"]'
        )

        modal = self.page.locator("#confirm_delete")
        expect(modal).to_be_visible()
        self.assertTrue(modal.is_visible())
        self.assertIn(
            "AI", modal.locator("#confirm-delete-homepage").inner_text()
        )
        self.assertIn(
            "English", modal.locator("#confirm-delete-lang").inner_text()
        )

    def test_cancel_does_not_delete_translation(self):
        self.page.goto(self.live_server_url + reverse("manage_homepages"))

        self.page.click(
            'button[title="Delete"][data-homepage="AI"][data-lang="English"]'
        )
        self.page.click('#confirm_delete button:has-text("Cancel")')

        self.page.reload()
        self.assertTrue(
            self.page.locator(
                'button[title="Delete"]'
                '[data-homepage="AI"][data-lang="English"]'
            ).is_visible()
        )

    def test_confirm_deletes_translation(self):
        self.page.goto(self.live_server_url + reverse("manage_homepages"))

        delete_button = self.page.locator(
            'button[title="Delete"][data-homepage="AI"][data-lang="English"]'
        )
        delete_button.click()

        modal = self.page.locator("#confirm_delete")
        expect(modal).to_be_visible()

        with self.page.expect_navigation():
            self.page.click("#confirm-delete-submit")

        expect(delete_button).not_to_be_visible()
