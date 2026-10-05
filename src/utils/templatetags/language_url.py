from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def language_url(context, language_code):
    request = context["request"]
    path = request.get_full_path()

    # Retire le préfixe de langue actuel
    for code, _ in settings.LANGUAGES:
        prefix = f"/{code}"

        if path == prefix or path.startswith(prefix + "/"):
            path = path[len(prefix):]
            break

    # Ajoute le nouveau préfixe
    return f"/{language_code}{path}"
