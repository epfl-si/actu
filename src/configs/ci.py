"""
Django specific settings for Continuous Integration.
"""

from .settings import *  # noqa

DEBUG = False

STATICFILES_DIRS = [
    BASE_DIR / "static",  # noqa: F405
]

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "manifest_path": BASE_DIR / "static" / "manifest.json",  # noqa: F405
    }
}

# Django Debug Toolbar can't be used with tests
DEBUG_TOOLBAR_CONFIG = {}

# When running tests remotely, ensure the Playwright version in your tests
# matches the version running in the Docker container.
# https://playwright.dev/docs/docker

REMOTE_PLAYWRIGHT_SERVER = "ws://playwright:3651"
