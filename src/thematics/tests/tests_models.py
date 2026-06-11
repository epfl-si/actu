from django.core.exceptions import ValidationError
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
            slug="ai",
        )

    def test_thematic_default_values(self):
        self.assertTrue(self.thematic.is_active)
        self.assertFalse(self.thematic.is_main)
        self.assertFalse(self.thematic.has_homepage)
        self.assertEqual(self.thematic.order, 0)

    def test_thematic_custom_values(self):
        custom_thematic = Thematic.objects.create(
            label_en="Health",
            label_fr="Santé",
            label_de="Gesundheit",
            label_it="Salute",
            slug="health",
            is_active=False,
            is_main=True,
            has_homepage=True,
            order=5,
        )
        self.assertFalse(custom_thematic.is_active)
        self.assertTrue(custom_thematic.is_main)
        self.assertTrue(custom_thematic.has_homepage)
        self.assertEqual(custom_thematic.order, 5)

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

    def test_slug_is_always_required(self):
        """Vérifie que Django bloque la validation si le slug est vide."""
        custom_thematic = Thematic(
            label_en="Energy",
            slug="",
        )

        with self.assertRaises(ValidationError) as context:
            custom_thematic.full_clean()

        self.assertIn("slug", context.exception.message_dict)
