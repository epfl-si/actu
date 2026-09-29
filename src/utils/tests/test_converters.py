from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from homepages.models import Homepage
from homepages.views import User
from topics.models import Topic


class ConvertersTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="niskanen",
            sciper="99999999",
        )
        self.topic = Topic.objects.create(
            label_en="AI",
            label_fr="IA",
        )
        self.homepage = Homepage.objects.create(
            slug="ai",
            topic=self.topic,
        )

    def test_invalid_language_gets_404(self):
        self.client.force_login(self.user)
        with self.assertRaises(NoReverseMatch):
            reverse(
                "create_homepage_translation",
                args=[self.homepage.id, "fi"],
            )
