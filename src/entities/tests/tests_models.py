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
            is_active=True,
            is_main=True,
            has_homepage=True,
            order=2,
        )
        self.assertTrue(custom_entity.is_active)
        self.assertTrue(custom_entity.is_main)
        self.assertTrue(custom_entity.has_homepage)
        self.assertEqual(custom_entity.order, 1)

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

    def test_inactive_or_not_main_forces_order_to_zero(self):
        """Verify that the order switches to 0 if the entity is not "
        "active or not in the main footer."""
        e1 = Entity.objects.create(
            label_en="ENAC", is_main=True, is_active=False, order=1
        )
        e2 = Entity.objects.create(
            label_en="SB", is_main=False, is_active=True, order=1
        )

        self.assertEqual(e1.order, 0)
        self.assertEqual(e2.order, 0)

    def test_reordering_on_insertion(self):
        """Verify that creating a new entity properly shifts the "
        "following ones."""
        self.entity.is_main = True
        self.entity.order = 1
        self.entity.save()

        e2 = Entity.objects.create(
            label_en="ENAC", is_main=True, is_active=True, order=2
        )
        e3 = Entity.objects.create(
            label_en="SB", is_main=True, is_active=True, order=2
        )

        e2.refresh_from_db()
        self.assertEqual(e3.order, 2)
        self.assertEqual(e2.order, 3)

    def test_reordering_on_deletion(self):
        """Verify that deleting an entity closes the ordering gaps."""
        self.entity.is_main = True
        self.entity.order = 1
        self.entity.save()

        e2 = Entity.objects.create(
            label_en="ENAC", is_main=True, is_active=True, order=2
        )
        e3 = Entity.objects.create(
            label_en="SB", is_main=True, is_active=True, order=3
        )

        e2.delete()
        e3.refresh_from_db()
        self.assertEqual(e3.order, 2)
