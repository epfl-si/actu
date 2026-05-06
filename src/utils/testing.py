import socket

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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
