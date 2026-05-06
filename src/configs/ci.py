"""
Django specific settings for Continuous Integration.
"""

from .settings import *  # noqa

DEBUG = False


# When running tests remotely, ensure the Playwright version in your tests
# matches the version running in the Docker container.
# https://playwright.dev/docs/docker

REMOTE_PLAYWRIGHT_SERVER = "ws://playwright:3651"
