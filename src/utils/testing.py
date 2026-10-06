import json
import os
import socket
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from playwright.sync_api import sync_playwright


class PlaywrightTestCase(StaticLiveServerTestCase):

    PLAYWRIGHT_CONNECT_TIMEOUT = 30000  # milliseconds

    @classmethod
    def setUpClass(cls):
        cls.host = cls._get_live_server_host()
        super().setUpClass()

        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.connect(
                settings.REMOTE_PLAYWRIGHT_SERVER,
                timeout=cls.PLAYWRIGHT_CONNECT_TIMEOUT,
                headers=cls._get_connect_headers(),
                slow_mo=cls._get_slow_mo(),
            )
        except Exception as exc:
            cls.playwright.stop()
            raise ConnectionError(
                f"Could not connect to Playwright server at "
                f"{settings.REMOTE_PLAYWRIGHT_SERVER!r}: {exc}"
            ) from exc

    @classmethod
    def _get_live_server_host(cls):
        """Return the host the live server should bind to.

        The browser may run on the same machine as Django or in a
        separate container (Docker/CI). We pick a host that is reachable from
        the configured Playwright server:

        - For a localhost remote server, bind to 127.0.0.1.
        - For a non-localhost remote server, bind to the container's network
          IP so the remote browser can reach Django.
        """
        remote_server = getattr(settings, "REMOTE_PLAYWRIGHT_SERVER", "")
        if remote_server and cls._is_local_address(remote_server):
            return "127.0.0.1"

        if remote_server:
            return socket.gethostbyname(socket.gethostname())

        # Fall back to Django's default when no remote server is configured.
        return cls.host

    @staticmethod
    def _is_local_address(url):
        """Return True if the given URL points to localhost."""
        try:
            hostname = urlparse(url).hostname
        except ValueError:
            return False
        return hostname in ("localhost", "127.0.0.1", "::1")

    @classmethod
    def _get_connect_headers(cls):
        """Build connect() headers from the environment.

        With PLAYWRIGHT_HEADED set, the remote server launches a headed
        browser, so the tests can be watched live on the host's display.
        """
        headers = {}
        if os.getenv("PLAYWRIGHT_HEADED"):
            headers["x-playwright-launch-options"] = json.dumps(
                {"headless": False}
            )
        return headers

    @staticmethod
    def _get_slow_mo():
        """Return the slow_mo for connect() from PLAYWRIGHT_SLOW_MO (ms)."""
        return float(os.getenv("PLAYWRIGHT_SLOW_MO", "0") or 0)

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
