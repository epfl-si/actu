from django.test import TestCase

from entities.models import Entity


class EntityModelTest(TestCase):

    def test_entity_creation_and_str(self):
        # Création de l'entité avec ses valeurs par défaut
        entity = Entity.objects.create(
            label_fr="FR", label_en="EN", label_de="DE", label_it="IT"
        )

        # Vérifications
        self.assertEqual(entity.label_fr, "FR")
        self.assertTrue(entity.is_active)
        self.assertFalse(entity.is_main)
        self.assertFalse(entity.has_homepage)
