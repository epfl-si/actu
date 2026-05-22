from django.test import TestCase

from entities.models import Entity


class EntityModelTest(TestCase):

    def test_entity_creation_and_str(self):
        # Création de l'entité avec ses valeurs par défaut
        entity = Entity.objects.create(label="SV")

        # Vérifications
        self.assertEqual(entity.label, "SV")
        self.assertTrue(entity.is_active)
        self.assertFalse(entity.is_main)
        self.assertFalse(entity.has_homepage)
        self.assertEqual(str(entity), "SV")
