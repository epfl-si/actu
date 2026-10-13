from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.urls import resolve
from django.utils import timezone, translation

from news.models import News
from news_formats.models import NewsFormat
from translations.models import NewsTranslation

User = get_user_model()


class LanguageUrlTagTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="iivo.niskanen",
            sciper="123456",
        )
        self.format, _ = NewsFormat.objects.get_or_create(
            id=1, defaults={"label_fr": "News de test"}
        )
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.fr = NewsTranslation.objects.create(
            news=self.news,
            language="fr",
            title="Ski de fond en Suisse",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
            created_by=self.user,
        )
        self.en = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            title="Cross-country skiing in Switzerland",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
            created_by=self.user,
        )
        self.de = NewsTranslation.objects.create(
            news=self.news,
            language="de",
            title="Langlauf in der Schweiz",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )
        self.factory = RequestFactory()

    def render_tag(self, path, language_code):
        template = Template("{% load language_url %}{% language_url code %}")
        request = self.factory.get(path)
        url_language = path.split("/")[1]
        with translation.override(url_language):
            request.resolver_match = resolve(path)
        return template.render(
            Context({"request": request, "code": language_code})
        )

    def test_news_page_returns_translated_news_url(self):
        url = self.render_tag(f"/fr/news/{self.fr.slug}/", "en")
        self.assertEqual(url, f"/en/news/{self.en.slug}/")

    def test_news_page_returns_home_when_translation_not_published(self):
        url = self.render_tag(f"/fr/news/{self.fr.slug}/", "de")
        self.assertEqual(url, "/de/")

    def test_news_page_returns_home_when_not_translated(self):
        url = self.render_tag(f"/fr/news/{self.fr.slug}/", "it")
        self.assertEqual(url, "/it/")

    def test_other_pages_swap_language_prefix(self):
        url = self.render_tag("/fr/news/", "en")
        self.assertEqual(url, "/en/news/")

    def test_news_page_tag_is_memoized_per_request(self):
        path = f"/fr/news/{self.fr.slug}/"
        template = Template(
            "{% load language_url %}"
            "{% language_url 'en' %}{% language_url 'it' %}"
            "{% language_url 'de' %}"
        )
        request = self.factory.get(path)
        # Emulates LocaleMiddleware: i18n_patterns only resolves the
        # active language's prefix.
        with translation.override("fr"):
            request.resolver_match = resolve(path)

        # First call fetches slug + siblings; the rest read the cache.
        with self.assertNumQueries(2):
            template.render(Context({"request": request}))


class PublicPageCacheSafetyTest(TestCase):

    def test_public_page_has_no_csrf_token(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "csrfmiddlewaretoken")
