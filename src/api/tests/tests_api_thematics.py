from django.test import TestCase
from django.urls import reverse

from thematics.models import Thematic


class ThematicAPITests(TestCase):

    def setUp(self):
        self.sl_thematic = Thematic.objects.create(
            label_en="Slalom",
            is_active=True,
            is_main=True,
            order=1,
        )
        self.dh_thematic = Thematic.objects.create(
            label_en="Downhill",
            is_active=False,
        )

        self.gs_thematic = Thematic.objects.create(
            label_en="Giant Slalom",
            is_active=True,
            is_main=False,
            order=0,
        )

    def test_list_thematics(self):
        url = reverse("thematic-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)

    def test_retrieve_inactive_thematic(self):
        url = reverse(
            "thematic-detail",
            kwargs={"version": "v1", "pk": self.dh_thematic.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_thematic(self):
        url = reverse(
            "thematic-detail",
            kwargs={"version": "v1", "pk": self.sl_thematic.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["label_en"], "Slalom")
        self.assertTrue(data["is_main"])
        self.assertEqual(data["order"], 1)

    def test_filter_thematics_by_is_main(self):
        url = reverse("thematic-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"is_main": "true"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "Slalom")

        response = self.client.get(url, {"is_main": "false"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "Giant Slalom")

    def test_search_thematics_by_label(self):
        url = reverse("thematic-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"search": "slalom"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["label_en"], "Slalom")

    def test_order_thematics(self):
        url = reverse("thematic-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"ordering": "order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["label_en"], "Giant Slalom")
        self.assertEqual(data["results"][1]["label_en"], "Slalom")

        response = self.client.get(url, {"ordering": "-order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["label_en"], "Slalom")
        self.assertEqual(data["results"][1]["label_en"], "Giant Slalom")
