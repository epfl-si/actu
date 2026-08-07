import socket

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from playwright.sync_api import sync_playwright


class PlaywrightTestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        super(StaticLiveServerTestCase, cls).setUpClass()

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.connect(
            settings.REMOTE_PLAYWRIGHT_SERVER
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def login_as(self, user):
        client = Client()
        client.force_login(user)
        sessionid = client.cookies["sessionid"]

        self.page.goto(self.live_server_url)

        self.context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": sessionid.value,
                    "url": self.live_server_url,
                }
            ]
        )
