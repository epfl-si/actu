"""
Django specific settings for OpenShift Container Platform.
"""

import logging
import os
from datetime import datetime

from .settings import *  # noqa

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = "/public/static"
MEDIA_ROOT = "/public/uploads"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # noqa: F405
]


# Enable hashing for static files
# This generates a staticfiles.json manifest that maps original filenames
# to their hashed versions.
# https://docs.djangoproject.com/en/5.2/ref/settings/#storages

MSFS = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STORAGES = {
    "staticfiles": {
        "BACKEND": MSFS,
    },
}

# Check to see if the user's id token has expired and if so, redirect to the
# OIDC provider's authentication endpoint for a silent re-auth.
MIDDLEWARE += ("mozilla_django_oidc.middleware.SessionRefresh",)  # noqa: F405

# Behind a proxy
# https://docs.djangoproject.com/en/5.2/ref/settings/#use-x-forwarded-host

USE_X_FORWARDED_HOST = True


# Custom HTTP header that tells Django whether the request came in via HTTPS
# https://docs.djangoproject.com/en/5.2/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django REST Framework
# Restrict production API responses to JSON only.

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]


class AuditLogDailyFileHandler(logging.FileHandler):
    """Custom FileHandler that create new file every day."""

    def __init__(self, folder, mode="a", encoding=None, delay=False):
        self.folder = folder
        filename = self._get_filename()
        super().__init__(filename, mode, encoding, delay)

    def _get_filename(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.folder, f"actu-audit-{date_str}.jsonl")

    def emit(self, record):
        current_file = self._get_filename()
        if self.baseFilename != os.path.abspath(current_file):
            if self.stream:
                self.stream.close()
                self.stream = None
            self.baseFilename = current_file
        super().emit(record)


AUDIT_LOG_FOLDER = os.getenv("ACTU_AUDIT_LOG_PATH")

if AUDIT_LOG_FOLDER:
    os.makedirs(AUDIT_LOG_FOLDER, exist_ok=True)

    handler_config = {
        "level": "INFO",
        "class": "configs.ocp.AuditLogDailyFileHandler",
        "folder": AUDIT_LOG_FOLDER,
        "formatter": "json_raw",
    }
else:
    handler_config = {
        "level": "INFO",
        "class": "logging.NullHandler",
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_raw": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "opdo_file": handler_config,
    },
    "loggers": {
        "opdo_audit": {
            "handlers": ["opdo_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
