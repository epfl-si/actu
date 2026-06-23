from django.test import TestCase
from django.utils import translation

from thematics.models import Thematic


class ThematicModelTest(TestCase):
    def setUp(self):
        self.thematic = Thematic.objects.create(
            label_en="AI",
            label_fr="IA",
            label_de="KI",
            label_it="IA",
        )

    def test_thematic_default_values(self):
        self.assertTrue(self.thematic.is_active)
        self.assertFalse(self.thematic.is_main)
        self.assertEqual(self.thematic.order, 0)

    def test_thematic_custom_values(self):
        custom_thematic = Thematic.objects.create(
            label_en="Health",
            label_fr="Santé",
            label_de="Gesundheit",
            label_it="Salute",
            is_active=True,
            is_main=True,
            order=1,
        )
        self.assertTrue(custom_thematic.is_active)
        self.assertTrue(custom_thematic.is_main)
        self.assertEqual(custom_thematic.order, 1)

    def test_inherited_get_label_method(self):
        self.assertEqual(self.thematic.get_label("en"), "AI")
        self.assertEqual(self.thematic.get_label("fr"), "IA")
        self.assertEqual(self.thematic.get_label("de"), "KI")
        self.assertEqual(self.thematic.get_label("it"), "IA")

    def test_inherited_str_changes_with_language(self):
        with translation.override("fr"):
            self.assertEqual(str(self.thematic), "IA")

        with translation.override("en"):
            self.assertEqual(str(self.thematic), "AI")

    def test_inactive_or_not_main_forces_order_to_zero(self):
        """Verify that the order is forced to 0 if not active or not "
        "in the main menu."""
        t1 = Thematic.objects.create(
            label_en="Energy", is_main=True, is_active=False, order=3
        )
        t2 = Thematic.objects.create(
            label_en="Climate", is_main=False, is_active=True, order=3
        )

        self.assertEqual(t1.order, 0)
        self.assertEqual(t2.order, 0)

    def test_reordering_on_insertion(self):
        """Verify that inserting a thematic properly shifts the others ("
        "bulk_update logic)."""
        self.thematic.is_main = True
        self.thematic.order = 1
        self.thematic.save()

        t2 = Thematic.objects.create(
            label_en="Health", is_main=True, is_active=True, order=2
        )

        t3 = Thematic.objects.create(
            label_en="Climate", is_main=True, is_active=True, order=2
        )

        t2.refresh_from_db()
        self.assertEqual(t3.order, 2)
        self.assertEqual(t2.order, 3)

    def test_reordering_on_deletion(self):
        """Verify that deleting a thematic closes the ordering gaps."""
        self.thematic.is_main = True
        self.thematic.order = 1
        self.thematic.save()

        t2 = Thematic.objects.create(
            label_en="Health", is_main=True, is_active=True, order=2
        )
        t3 = Thematic.objects.create(
            label_en="Climate", is_main=True, is_active=True, order=3
        )

        t2.delete()
        t3.refresh_from_db()
        self.assertEqual(t3.order, 2)
