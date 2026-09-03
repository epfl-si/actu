from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from api.pagination import NewsPagination
from entities.models import Entity
from news.models import News
from news_formats.models import NewsFormat
from thematics.models import Thematic
from translations.models import NewsTranslation

User = get_user_model()


class NewsAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.get(id=1)
        self.thematic = Thematic.objects.create(
            label_en="AI",
            is_active=True,
        )
        self.other_thematic = Thematic.objects.create(
            label_en="Health",
            is_active=True,
        )
        self.entity = Entity.objects.create(
            label_en="SV",
            is_active=True,
        )
        self.other_entity = Entity.objects.create(
            label_en="ENAC",
            is_active=True,
        )

        self.now = timezone.now()

    def _create_news(
        self,
        title,
        thematic=None,
        entity=None,
        published_at=None,
        status=None,
    ):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        if thematic:
            news.thematics.add(thematic)
        if entity:
            news.entities.add(entity)
        translation = NewsTranslation.objects.create(
            news=news,
            language="en",
            title=title,
            status=status or NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            published_at=published_at,
            published_by=self.user,
        )
        return news, translation

    def test_list_news_by_thematic(self):
        for i in range(5):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["results"][0]["title"], "News 0")

    def test_filters_by_thematic(self):
        self._create_news(
            title="Thematic news",
            thematic=self.thematic,
            published_at=self.now,
        )
        self._create_news(
            title="Other thematic news",
            thematic=self.other_thematic,
            published_at=self.now,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Thematic news")

    def test_list_news_by_entity(self):
        for i in range(5):
            self._create_news(
                title=f"Entity news {i}",
                entity=self.entity,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"entity": self.entity.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["results"][0]["title"], "Entity news 0")

    def test_filters_by_entity(self):
        self._create_news(
            title="Entity news",
            entity=self.entity,
            published_at=self.now,
        )
        self._create_news(
            title="Other entity news",
            entity=self.other_entity,
            published_at=self.now,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"entity": self.entity.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Entity news")

    def test_returns_news_without_filter(self):
        for i in range(5):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["results"][0]["title"], "News 0")

    def test_rejects_both_thematic_and_entity_parameters(self):
        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "entity": self.entity.pk},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_respects_language(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.thematics.add(self.thematic)
        NewsTranslation.objects.create(
            news=news,
            language="en",
            title="English title",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            published_at=self.now,
            published_by=self.user,
        )
        NewsTranslation.objects.create(
            news=news,
            language="fr",
            title="Titre français",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            published_at=self.now,
            published_by=self.user,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "language": "fr"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Titre français")

    def test_excludes_non_published_statuses(self):
        self._create_news(
            title="Draft news",
            thematic=self.thematic,
            published_at=self.now,
            status=NewsTranslation.Status.DRAFT,
        )
        self._create_news(
            title="Archived news",
            thematic=self.thematic,
            published_at=self.now,
            status=NewsTranslation.Status.ARCHIVED,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 0)

    def test_excludes_unpublished_news(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.thematics.add(self.thematic)
        NewsTranslation.objects.create(
            news=news,
            language="en",
            title="Unpublished news",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            published_at=None,
            published_by=self.user,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 0)

    def test_returns_format_in_requested_language(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.thematics.add(self.thematic)
        NewsTranslation.objects.create(
            news=news,
            language="fr",
            title="Titre français",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            published_at=self.now,
            published_by=self.user,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "language": "fr"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["format"], self.format.label_fr)

    def test_format_defaults_to_english_label(self):
        self._create_news(
            title="News with format",
            thematic=self.thematic,
            published_at=self.now,
        )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["format"], self.format.label_en)

    def test_limit_parameter_changes_page_size(self):
        for i in range(5):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "limit": 2},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["title"], "News 0")
        self.assertEqual(data["results"][1]["title"], "News 1")

    def test_pagination_returns_requested_page(self):
        for i in range(5):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "limit": 2, "page": 2},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["title"], "News 2")
        self.assertEqual(data["results"][1]["title"], "News 3")
        self.assertEqual(data["count"], 5)
        self.assertIsNotNone(data["previous"])
        self.assertIsNotNone(data["next"])

    def test_pagination_includes_count_and_navigation(self):
        for i in range(4):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(
            url,
            {"thematic": self.thematic.pk, "limit": 3},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 4)
        self.assertEqual(len(data["results"]), 3)
        self.assertIsNone(data["previous"])
        self.assertIsNotNone(data["next"])

    def test_default_page_size_matches_settings(self):
        page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        total = page_size + 2

        for i in range(total):
            self._create_news(
                title=f"News {i}",
                thematic=self.thematic,
                published_at=self.now - timedelta(days=i),
            )

        url = reverse("news-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"thematic": self.thematic.pk})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), page_size)
        self.assertEqual(data["count"], total)
        self.assertIsNone(data["previous"])
        self.assertIsNotNone(data["next"])


class NewsPaginationTests(TestCase):

    def test_page_size_matches_rest_framework_settings(self):
        self.assertEqual(
            NewsPagination.page_size,
            settings.REST_FRAMEWORK["PAGE_SIZE"],
        )
