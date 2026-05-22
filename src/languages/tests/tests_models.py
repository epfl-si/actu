from django.db import IntegrityError
from django.test import TestCase

from languages.models import Language


class LanguageModelTest(TestCase):

    def test_language_creation_and_str(self):
        lang = Language.objects.create(language="fr")

        self.assertEqual(lang.language, "fr")
        self.assertEqual(str(lang), "fr")

    def test_language_unicity_constraint(self):
        Language.objects.create(language="FR")

        with self.assertRaises(IntegrityError):
            Language.objects.create(language="FR")
