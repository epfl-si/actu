from django.test import TestCase

from thematics.models import Thematic


class ThematicModelTest(TestCase):

    def test_thematic_creation_and_str(self):
        thematic = Thematic.objects.create(
            label_en="AI",
            label_fr="IA",
            label_de="AI",
            label_it="AI",
            order=1,
        )

        self.assertEqual(thematic.label_en, "AI")
        self.assertEqual(thematic.order, 1)
        self.assertFalse(thematic.has_homepage)
