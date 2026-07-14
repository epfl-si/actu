from django.contrib.auth import get_user_model
from django.test import TestCase

from entities.models import Entity
from news.models import News
from news_formats.models import NewsFormat
from thematics.models import Thematic

User = get_user_model()


class NewsModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="niskanen",
            password="99999999",
        )
        self.format, _ = NewsFormat.objects.get_or_create(
            id=1, defaults={"label_fr": "News de test"}
        )
        self.thematic = Thematic.objects.create(
            label_fr="Ski de fond",
            label_en="Cross-Country Skiing",
            label_de="Langlauf",
            label_it="Sci di fondo",
        )
        self.entity = Entity.objects.create(
            label_fr="Équipe de Finlande",
            label_en="Team Finland",
            label_de="Team Finnland",
            label_it="Team Finlandia",
        )
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )

    def test_str_returns_news_id(self):
        self.assertEqual(str(self.news), f"News #{self.news.pk}")

    def test_can_add_thematic(self):
        self.news.thematics.add(self.thematic)
        self.assertIn(self.thematic, self.news.thematics.all())

    def test_can_add_entity(self):
        self.news.entities.add(self.entity)
        self.assertIn(self.entity, self.news.entities.all())

    def test_entities_is_optional(self):
        self.assertEqual(self.news.entities.count(), 0)

    def test_thematics_is_optional(self):
        self.assertEqual(self.news.thematics.count(), 0)

    def test_created_by_is_set(self):
        self.assertEqual(self.news.created_by, self.user)

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.news.created_at)

    def test_ordering_is_by_created_at_descending(self):
        news2 = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news_list = list(News.objects.all())
        self.assertEqual(news_list[0], news2)
        self.assertEqual(news_list[1], self.news)
