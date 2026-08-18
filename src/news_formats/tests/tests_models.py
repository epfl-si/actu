from django.test import TestCase

from block_types.models import BlockType
from news_formats.models import NewsFormat


class NewsFormatModelTest(TestCase):

    def setUp(self):
        self.block = BlockType.objects.create(
            label_fr="Test Block", label_en="Test Block EN"
        )

        self.news_format = NewsFormat.objects.create(
            label_fr="Test Format", label_en="Test Format", icon="#test-icon"
        )
        self.news_format.allowed_blocks.add(self.block)

    def test_news_format_creation(self):
        self.assertEqual(self.news_format.label_fr, "Test Format")
        self.assertEqual(self.news_format.icon, "#test-icon")

    def test_news_format_allowed_blocks_relation(self):
        self.assertEqual(self.news_format.allowed_blocks.count(), 1)
        self.assertIn(self.block, self.news_format.allowed_blocks.all())

    def test_string_representation(self):
        self.assertEqual(str(self.news_format), "Test Format")
