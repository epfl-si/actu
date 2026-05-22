from django.test import TestCase

from thematics.models import Thematic


class ThematicModelTest(TestCase):

    def test_thematic_creation_and_str(self):
        thematic = Thematic.objects.create(
            label="AI",
            order=1,
        )

        self.assertEqual(thematic.label, "AI")
        self.assertEqual(thematic.order, 1)
        self.assertTrue(thematic.has_homepage)
        self.assertEqual(str(thematic), "AI")
