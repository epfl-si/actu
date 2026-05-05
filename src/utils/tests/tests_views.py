from django.test import TestCase
from django.urls import reverse


class UtilsViewsTests(TestCase):

    def test_healthz(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK", response.content.decode())
