from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.timezone import localtime, now

from entities.models import Entity
from homepages.models import Homepage, HomepageTranslation
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


class HomepageTranslationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="vonallmen",
            sciper="99999999",
            first_name="Franjo",
            last_name="Von Allmen",
        )
        self.thematic = Thematic.objects.create(
            label_en="AI",
            label_fr="IA",
        )
        self.homepage = Homepage.objects.create(
            slug="ai",
            thematic=self.thematic,
        )
        self.translation = HomepageTranslation.objects.create(
            homepage=self.homepage,
            language="en",
            status=HomepageTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_str(self):
        self.assertEqual(
            str(self.translation),
            "AI [en]",
        )

    def test_default_status_is_draft(self):
        self.assertEqual(
            self.translation.status, HomepageTranslation.Status.DRAFT
        )

    def test_is_published_false_when_draft(self):
        self.assertFalse(self.translation.is_published)

    def test_is_published_true_when_published(self):
        self.translation.status = HomepageTranslation.Status.PUBLISHED
        self.translation.save()
        self.assertTrue(self.translation.is_published)

    def test_unique_together_homepage_and_language(self):
        with self.assertRaises(Exception):
            HomepageTranslation.objects.create(
                homepage=self.homepage,
                language="en",
                created_by=self.user,
            )

    def test_can_create_different_language_translation(self):
        HomepageTranslation.objects.create(
            homepage=self.homepage,
            language="fr",
            created_by=self.user,
        )
        self.assertEqual(
            HomepageTranslation.objects.filter(homepage=self.homepage).count(),
            2,
        )

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.translation.created_at)

    def test_created_by_is_set(self):
        self.assertEqual(self.translation.created_by, self.user)

    def test_updated_at_is_set(self):
        self.assertIsNotNone(self.translation.updated_at)

    def test_updated_by_is_none_by_default(self):
        self.assertIsNone(self.translation.updated_by)

    def test_published_at_is_none_by_default(self):
        self.assertIsNone(self.translation.published_at)

    def test_published_by_is_none_by_default(self):
        self.assertIsNone(self.translation.published_by)

    def test_last_activity_label_for_draft_without_update(self):
        label = self.translation.last_activity_label
        expected_date = localtime(self.translation.created_at).strftime(
            "%d.%m.%Y %H:%M"
        )
        self.assertIn("Created", label)
        self.assertIn(expected_date, label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)

    def test_last_activity_label_for_draft_with_update(self):
        other_user = User.objects.create(
            username="niskanen",
            sciper="88888888",
            first_name="Iivo",
            last_name="Niskanen",
        )
        self.translation.updated_by = other_user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Updated", label)
        self.assertIn("Iivo Niskanen", label)

    def test_last_activity_label_for_published(self):
        self.translation.status = HomepageTranslation.Status.PUBLISHED
        self.translation.published_at = now()
        self.translation.published_by = self.user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Published", label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)

    def test_last_activity_label_for_archived(self):
        self.translation.status = HomepageTranslation.Status.ARCHIVED
        self.translation.updated_by = self.user
        self.translation.save()

        label = self.translation.last_activity_label

        self.assertIn("Archived", label)
        self.assertIn(f"{self.user.first_name} {self.user.last_name}", label)
