from django.test import TestCase
from django.urls import reverse

from api.filters import EntityFilter
from entities.models import Entity


class EntityAPITests(TestCase):

    def setUp(self):
        self.st_entity = Entity.objects.create(
            label_en="Streif",  # Kitzbühel
            is_active=True,
            is_main=True,
            order=1,
        )
        self.sa_entity = Entity.objects.create(
            label_en="Saslong",  # Val Gardena
            is_active=False,
        )

        self.la_entity = Entity.objects.create(
            label_en="Lauberhorn",  # Wengen
            is_active=True,
            is_main=False,
            order=0,
        )

    def test_list_entities(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)

    def test_retrieve_inactive_entity(self):
        url = reverse(
            "entity-detail",
            kwargs={"version": "v1", "pk": self.sa_entity.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_entity(self):
        url = reverse(
            "entity-detail",
            kwargs={"version": "v1", "pk": self.st_entity.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["label_en"], "Streif")
        self.assertTrue(data["is_main"])
        self.assertEqual(data["order"], 1)

    def test_filter_entities_by_is_main(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"is_main": "true"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "Streif")

        response = self.client.get(url, {"is_main": "false"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "Lauberhorn")

    def test_search_entities_by_label(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"search": "horn"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "Lauberhorn")

    def test_order_entities(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"ordering": "order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["label_en"], "Lauberhorn")
        self.assertEqual(data["results"][1]["label_en"], "Streif")

        response = self.client.get(url, {"ordering": "-order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["label_en"], "Streif")
        self.assertEqual(data["results"][1]["label_en"], "Lauberhorn")

    def test_filter_search_with_whitespace(self):
        queryset = Entity.objects.filter(is_active=True)
        filterset = EntityFilter(queryset=queryset, data={})
        result = filterset.filter_search(queryset, "search", " ")
        self.assertEqual(list(result), list(queryset))
