from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.translation import override

from translations.models import NewsTranslation

register = template.Library()


def get_default_url_path(request, language_code):
    # Default behavior for other pages
    path = request.get_full_path()

    for code, _ in settings.LANGUAGES:
        prefix = f"/{code}"

        if path == prefix or path.startswith(prefix + "/"):
            path = path[len(prefix) :]
            break

    return f"/{language_code}{path}"


def get_published_slugs_for_a_news(slug):
    # get a dict with languages as keys and slugs as values
    news_id = (
        NewsTranslation.objects.filter(
            slug=slug,
            status=NewsTranslation.Status.PUBLISHED,
        )
        .values_list("news_id", flat=True)
        .first()
    )

    if news_id:
        return dict(
            NewsTranslation.objects.filter(
                news_id=news_id,
                status=NewsTranslation.Status.PUBLISHED,
            ).values_list("language", "slug")
        )

    return None


@register.simple_tag(takes_context=True)
def language_url(context, language_code):
    request = context["request"]
    resolver_match = request.resolver_match

    # special case when viewing the News detail page,
    # as it need a cache (the menu calls this tag once per language)
    if (
        resolver_match
        and resolver_match.url_name == "view_news"
        and resolver_match.kwargs.get("slug")
    ):
        # Menu calls this tag once per language; cache the lookups
        # for the whole render.
        languages_and_slugs = getattr(request, "_published_slugs", None)

        if not languages_and_slugs:
            # no cache found. Let's fulfill it
            languages_and_slugs = get_published_slugs_for_a_news(
                resolver_match.kwargs.get("slug")
            )
            request._published_slugs = languages_and_slugs

        with override(language_code):
            translated_slug = languages_and_slugs.get(language_code)

            if translated_slug:
                return reverse(
                    "view_news",
                    kwargs={"slug": translated_slug},
                )

            return reverse("homepages")
    else:
        # default behavior for the other pages
        return get_default_url_path(request, language_code)
