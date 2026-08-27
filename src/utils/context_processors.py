from django.conf import settings


def get_default_lang(request):
    return {"get_default_lang": settings.LANGUAGES[0][0]}
