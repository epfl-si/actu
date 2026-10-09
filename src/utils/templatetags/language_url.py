from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.translation import override

from translations.models import NewsTranslation

register = template.Library()


@register.simple_tag(takes_context=True)
def language_url(context, language_code):
    request = context["request"]
    resolver_match = request.resolver_match

    # News detail page
    if resolver_match and resolver_match.url_name == "view_news":
        slug = resolver_match.kwargs.get("slug")

        if slug:
            # Menu calls this tag once per language; cache the lookups
            # for the whole render.
            published_translations = getattr(
                request, "_language_url_translations", None
            )
            if published_translations is None:
                translation = NewsTranslation.objects.filter(
                    slug=slug,
                    status=NewsTranslation.Status.PUBLISHED,
                ).first()

                if translation:
                    published_translations = {
                        t.language: t
                        for t in NewsTranslation.objects.filter(
                            news_id=translation.news_id,
                            status=NewsTranslation.Status.PUBLISHED,
                        )
                    }
                    request._language_url_translations = published_translations

            if published_translations:
                with override(language_code):
                    translated = published_translations.get(language_code)

                    if translated:
                        return reverse(
                            "view_news",
                            kwargs={"slug": translated.slug},
                        )

                    return reverse("homepages")

    # Default behaviour for other pages
    path = request.get_full_path()

    for code, _ in settings.LANGUAGES:
        prefix = f"/{code}"

        if path == prefix or path.startswith(prefix + "/"):
            path = path[len(prefix) :]
            break

    return f"/{language_code}{path}"
