"""
Django specific settings for OpenShift Container Platform.
"""

from .settings import *  # noqa

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = "/public/static"


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


# Behind a proxy
# https://docs.djangoproject.com/en/5.2/ref/settings/#use-x-forwarded-host

USE_X_FORWARDED_HOST = True


# Custom HTTP header that tells Django whether the request came in via HTTPS
# https://docs.djangoproject.com/en/5.2/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
