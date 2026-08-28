import socket

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from playwright.sync_api import sync_playwright


class PlaywrightTestCase(StaticLiveServerTestCase):

    PLAYWRIGHT_CONNECT_TIMEOUT = 30000  # milliseconds

    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        super().setUpClass()

        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.connect(
                settings.REMOTE_PLAYWRIGHT_SERVER,
                timeout=cls.PLAYWRIGHT_CONNECT_TIMEOUT,
            )
        except Exception as exc:
            cls.playwright.stop()
            raise ConnectionError(
                f"Could not connect to Playwright server at "
                f"{settings.REMOTE_PLAYWRIGHT_SERVER!r}: {exc}"
            ) from exc

    @classmethod
    def tearDownClass(cls):
        try:
            browser = getattr(cls, "browser", None)
            if browser is not None:
                browser.close()
        finally:
            playwright = getattr(cls, "playwright", None)
            if playwright is not None:
                playwright.stop()
            super().tearDownClass()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        # Dismiss the cookie consent banner.
        self.context.add_cookies(
            [
                {
                    "name": "petitpois",
                    "value": "dismiss",
                    "url": self.live_server_url,
                }
            ]
        )

    def tearDown(self):
        context = getattr(self, "context", None)
        if context is not None:
            context.close()

    def login_as(self, user):
        client = Client()
        client.force_login(user)
        sessionid = client.cookies["sessionid"]

        self.context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": sessionid.value,
                    "url": self.live_server_url,
                }
            ]
        )
