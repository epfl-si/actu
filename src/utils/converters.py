from configs import settings


class LanguageConverter:
    language_codes = [code for code, name in settings.LANGUAGES]
    regex = "|".join(language_codes)

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)
