from django.test import TestCase
from django.utils import translation

from topics.models import Topic


class TopicModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(
            label_en="AI",
            label_fr="IA",
            label_de="KI",
            label_it="IA",
        )

    def test_topic_default_values(self):
        self.assertTrue(self.topic.is_active)
        self.assertFalse(self.topic.is_main)
        self.assertEqual(self.topic.order, 0)

    def test_topic_custom_values(self):
        custom_topic = Topic.objects.create(
            label_en="Health",
            label_fr="Santé",
            label_de="Gesundheit",
            label_it="Salute",
            is_active=True,
            is_main=True,
            order=1,
        )
        self.assertTrue(custom_topic.is_active)
        self.assertTrue(custom_topic.is_main)
        self.assertEqual(custom_topic.order, 1)

    def test_inherited_get_label_method(self):
        self.assertEqual(self.topic.get_label("en"), "AI")
        self.assertEqual(self.topic.get_label("fr"), "IA")
        self.assertEqual(self.topic.get_label("de"), "KI")
        self.assertEqual(self.topic.get_label("it"), "IA")

    def test_inherited_str_changes_with_language(self):
        with translation.override("fr"):
            self.assertEqual(str(self.topic), "IA")

        with translation.override("en"):
            self.assertEqual(str(self.topic), "AI")

    def test_inactive_or_not_main_forces_order_to_zero(self):
        """Verify that the order is forced to 0 if not active or not "
        "in the main menu."""
        t1 = Topic.objects.create(
            label_en="Energy", is_main=True, is_active=False, order=3
        )
        t2 = Topic.objects.create(
            label_en="Climate", is_main=False, is_active=True, order=3
        )

        self.assertEqual(t1.order, 0)
        self.assertEqual(t2.order, 0)

    def test_reordering_on_insertion(self):
        """Verify that inserting a topic properly shifts the others ("
        "bulk_update logic)."""
        self.topic.is_main = True
        self.topic.order = 1
        self.topic.save()

        t2 = Topic.objects.create(
            label_en="Health", is_main=True, is_active=True, order=2
        )

        t3 = Topic.objects.create(
            label_en="Climate", is_main=True, is_active=True, order=2
        )

        t2.refresh_from_db()
        self.assertEqual(t3.order, 2)
        self.assertEqual(t2.order, 3)

    def test_reordering_on_deletion(self):
        """Verify that deleting a topic closes the ordering gaps."""
        self.topic.is_main = True
        self.topic.order = 1
        self.topic.save()

        t2 = Topic.objects.create(
            label_en="Health", is_main=True, is_active=True, order=2
        )
        t3 = Topic.objects.create(
            label_en="Climate", is_main=True, is_active=True, order=3
        )

        t2.delete()
        t3.refresh_from_db()
        self.assertEqual(t3.order, 2)
