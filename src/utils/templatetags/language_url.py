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
    if resolver_match and resolver_match.url_name == "news_detail":
        slug = resolver_match.kwargs.get("slug")

        if slug:
            translation = (
                NewsTranslation.objects.filter(
                    slug=slug,
                    status=NewsTranslation.Status.PUBLISHED,
                )
                .select_related("news")
                .first()
            )

            if translation:
                translated = translation.news.translations.filter(
                    language=language_code,
                    status=NewsTranslation.Status.PUBLISHED,
                ).first()

                with override(language_code):
                    if translated:
                        return reverse(
                            "news_detail",
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
