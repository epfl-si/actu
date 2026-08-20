from django.test import TestCase
from django.urls import reverse

from entities.models import Entity


class EntityAPITests(TestCase):

    def setUp(self):
        self.sv_entity = Entity.objects.create(
            label_en="School of Science",
            is_active=True,
            is_main=True,
            order=1,
        )
        self.sb_entity = Entity.objects.create(
            label_en="School of Business",
            is_active=False,
        )

        self.enac_entity = Entity.objects.create(
            label_en="School of Architecture",
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
            kwargs={"version": "v1", "pk": self.sb_entity.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_entity(self):
        url = reverse(
            "entity-detail",
            kwargs={"version": "v1", "pk": self.sv_entity.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["label_en"], "School of Science")
        self.assertTrue(data["is_main"])
        self.assertEqual(data["order"], 1)

    def test_filter_entities_by_is_main(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"is_main": "true"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["label_en"], "School of Science")

        response = self.client.get(url, {"is_main": "false"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(
            data["results"][0]["label_en"], "School of Architecture"
        )

    def test_search_entities_by_label(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"search": "school"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["label_en"], "School of Science")

    def test_order_entities(self):
        url = reverse("entity-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"ordering": "order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["results"][0]["label_en"], "School of Architecture"
        )
        self.assertEqual(data["results"][1]["label_en"], "School of Science")

        response = self.client.get(url, {"ordering": "-order"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"][0]["label_en"], "School of Science")
        self.assertEqual(
            data["results"][1]["label_en"], "School of Architecture"
        )
