from django.test import TestCase
from django.utils import translation

from languages.models import Language


class LanguageModelTest(TestCase):

    def setUp(self):
        self.language = Language.objects.create(
            label_fr="Anglais",
            label_en="English",
            label_de="Englisch",
            label_it="Inglese",
            code="en",
        )

    def test_inherited_get_label_method(self):
        self.assertEqual(self.language.get_label("fr"), "Anglais")
        self.assertEqual(self.language.get_label("en"), "English")
        self.assertEqual(self.language.get_label("de"), "Englisch")
        self.assertEqual(self.language.get_label("it"), "Inglese")

    def test_inherited_str_changes_with_language(self):
        with translation.override("fr"):
            self.assertEqual(str(self.language), "Anglais")

        with translation.override("en"):
            self.assertEqual(str(self.language), "English")
