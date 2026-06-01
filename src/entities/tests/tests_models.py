from django.test import TestCase
from django.utils import translation

from entities.models import Entity


class EntityModelTest(TestCase):

    def setUp(self):
        self.entity = Entity.objects.create(
            label_en="Life Sciences",
            label_fr="Sciences de la Vie",
            label_de="Lebenswissenschaften",
            label_it="Scienze della Vita",
        )

    def test_entity_default_values(self):
        self.assertTrue(self.entity.is_active)
        self.assertFalse(self.entity.is_main)
        self.assertFalse(self.entity.has_homepage)
        self.assertEqual(self.entity.order, 0)

    def test_entity_custom_values(self):
        custom_entity = Entity.objects.create(
            label_en="Basic Sciences",
            label_fr="Sciences de Base",
            label_de="Grundlagenwissenschaften",
            label_it="Scienze di Base",
            is_active=False,
            is_main=True,
            has_homepage=True,
            order=2,
        )
        self.assertFalse(custom_entity.is_active)
        self.assertTrue(custom_entity.is_main)
        self.assertTrue(custom_entity.has_homepage)
        self.assertEqual(custom_entity.order, 2)

    def test_inherited_get_label_method(self):
        self.assertEqual(self.entity.get_label("fr"), "Sciences de la Vie")
        self.assertEqual(self.entity.get_label("en"), "Life Sciences")
        self.assertEqual(self.entity.get_label("de"), "Lebenswissenschaften")
        self.assertEqual(self.entity.get_label("it"), "Scienze della Vita")

    def test_inherited_str_changes_with_language(self):
        with translation.override("fr"):
            self.assertEqual(str(self.entity), "Sciences de la Vie")

        with translation.override("en"):
            self.assertEqual(str(self.entity), "Life Sciences")
