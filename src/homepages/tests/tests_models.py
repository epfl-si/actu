from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from entities.models import Entity
from homepages.models import Homepage
from thematics.models import Thematic

User = get_user_model()


class HomepageModelTest(TestCase):
    def setUp(self):
        self.thematic = Thematic.objects.create(
            label_en="Artificial Intelligence",
            label_fr="Intelligence Artificielle",
        )

        self.entity = Entity.objects.create(
            label_en="Basic Sciences",
            label_fr="Sciences de Base",
        )

    def test_create_homepage_with_thematic_only(self):
        homepage = Homepage.objects.create(
            slug="ai-home", thematic=self.thematic
        )

        homepage.full_clean()

        self.assertEqual(homepage.thematic, self.thematic)
        self.assertIsNone(homepage.entity)

    def test_create_homepage_with_entity_only(self):
        homepage = Homepage.objects.create(slug="sb-home", entity=self.entity)

        homepage.full_clean()

        self.assertEqual(homepage.entity, self.entity)
        self.assertIsNone(homepage.thematic)

    def test_clean_raises_error_if_both_relations_are_set(self):
        homepage = Homepage(
            slug="invalid-home",
            thematic=self.thematic,
            entity=self.entity,
        )

        with self.assertRaises(ValidationError) as context:
            homepage.full_clean()

        self.assertTrue(
            any(
                "cannot be linked to both" in str(err)
                for err in context.exception.messages
            )
        )

    def test_clean_raises_error_if_no_relation_is_set(self):
        homepage = Homepage(slug="invalid-home")

        with self.assertRaises(ValidationError) as context:
            homepage.full_clean()

        self.assertTrue(
            any(
                "must be linked to either" in str(err)
                for err in context.exception.messages
            )
        )

    def test_db_constraint_blocks_both_relations(self):
        with self.assertRaises(IntegrityError):
            Homepage.objects.create(
                slug="invalid-home",
                thematic=self.thematic,
                entity=self.entity,
            )

    def test_db_constraint_blocks_no_relation(self):
        with self.assertRaises(IntegrityError):
            Homepage.objects.create(slug="invalid-home")
