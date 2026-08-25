class LanguageConverter:
    regex = "en|fr|it|de"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)
