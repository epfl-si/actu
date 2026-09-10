"""
Django specific settings for OpenShift Container Platform.
"""

from .settings import *  # noqa

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = "/public/static"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # noqa: F405
    BASE_DIR / "utils" / "static",  # noqa: F405
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
