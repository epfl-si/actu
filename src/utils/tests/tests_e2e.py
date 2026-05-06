from playwright.sync_api import expect

from utils.testing import PlaywrightTestCase


class UtilsPlaywrightTests(PlaywrightTestCase):

    def test_healthz(self):

        self.page.goto(self.live_server_url + "/healthz/")

        expect(self.page).to_have_title("")
        expect(self.page.locator("body")).to_have_text("OK")

    def test_foobar(self):

        self.page.goto(self.live_server_url + "/foobar/")

        expect(self.page).to_have_title("Not Found")
        expect(self.page.locator("p")).to_have_text(
            "The requested resource was not found on this server."
        )
