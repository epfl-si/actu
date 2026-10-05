"""
Django specific settings for OpenShift Container Platform.
"""

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

AUDIT_LOG_FOLDER = os.getenv("ACTU_AUDIT_LOG_PATH")

if AUDIT_LOG_FOLDER:
    os.makedirs(AUDIT_LOG_FOLDER, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"actu-audit-{date}.jsonl"
    AUDIT_LOG_FILE_PATH = os.path.join(AUDIT_LOG_FOLDER, file_name)

    handler_config = {
        "level": "INFO",
        "class": "logging.FileHandler",
        "filename": AUDIT_LOG_FILE_PATH,
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
