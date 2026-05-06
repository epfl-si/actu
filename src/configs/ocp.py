"""
Django specific settings for OpenShift Container Platform.
"""

from .settings import *  # noqa

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = "/public/static"
