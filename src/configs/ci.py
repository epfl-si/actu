"""
Django specific settings for Continuous Integration.
"""

from .settings import *  # noqa

DEBUG = False

DJANGO_VITE = {
    "default": {
        "dev_mode": True,
        "dev_server_host": "assets",
        "dev_server_port": 5173,
    }
}

# Django Debug Toolbar can't be used with tests
DEBUG_TOOLBAR_CONFIG = {}

# When running tests remotely, ensure the Playwright version in your tests
# matches the version running in the Docker container.
# https://playwright.dev/docs/docker

REMOTE_PLAYWRIGHT_SERVER = "ws://playwright:3651"
