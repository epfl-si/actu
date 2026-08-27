from django.conf import settings


class APIVersionConverter:
    regex = "|".join(settings.REST_FRAMEWORK["ALLOWED_VERSIONS"])

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
