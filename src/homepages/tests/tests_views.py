from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class HomepagesViewsTests(TestCase):

    def test_title_homepage_fr(self):
        with translation.override("fr"):
            response = self.client.get(reverse("homepages"))
            self.assertEqual(200, response.status_code)
            self.assertIn(
                "<title>Actualités - EPFL</title>",
                response.content.decode(),
            )
