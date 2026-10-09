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
                news_id = (
                    NewsTranslation.objects.filter(
                        slug=slug,
                        status=NewsTranslation.Status.PUBLISHED,
                    )
                    .values_list("news_id", flat=True)
                    .first()
                )

                if news_id:
                    published_translations = dict(
                        NewsTranslation.objects.filter(
                            news_id=news_id,
                            status=NewsTranslation.Status.PUBLISHED,
                        ).values_list("language", "slug")
                    )
                    request._language_url_translations = published_translations

            if published_translations:
                with override(language_code):
                    translated_slug = published_translations.get(language_code)

                    if translated_slug:
                        return reverse(
                            "view_news",
                            kwargs={"slug": translated_slug},
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
