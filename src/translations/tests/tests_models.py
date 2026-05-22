from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from entities.models import Entity
from languages.models import Language
from translations.models import Translation


class TranslationModelTest(TestCase):
    def setUp(self):
        self.language_fr = Language.objects.create(language="fr")
        self.language_en = Language.objects.create(language="en")
        self.entity = Entity.objects.create(label="SB")
        self.entity_content_type = ContentType.objects.get_for_model(Entity)

    def test_translation_creation(self):
        translation = Translation.objects.create(
            content_type=self.entity_content_type,
            object_id=self.entity.id,
            language=self.language_fr,
            translation="Faculté des sciences de base",
        )

        self.assertEqual(
            translation.translation, "Faculté des sciences de base"
        )
        self.assertEqual(translation.content_object, self.entity)

    def test_unique_translation_per_object_language_constraint(self):
        Translation.objects.create(
            content_type=self.entity_content_type,
            object_id=self.entity.id,
            language=self.language_fr,
            translation="Premier essai",
        )

        with self.assertRaises(IntegrityError):
            Translation.objects.create(
                content_type=self.entity_content_type,
                object_id=self.entity.id,
                language=self.language_fr,
                translation="Doublon interdit !",
            )
