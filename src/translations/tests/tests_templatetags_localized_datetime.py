from datetime import date, datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from translations.templatetags.translation_tags import localized_datetime


class LocalizedDatetimeTests(TestCase):
    @staticmethod
    def make_datetime(value):
        return timezone.make_aware(
            datetime.combine(
                value, datetime.min.time().replace(hour=14, minute=30)
            )
        )

    @patch("translations.templatetags.translation_tags.gettext")
    def test_empty_value_returns_empty_string(self, mock_gettext):
        self.assertEqual(localized_datetime(None, "published"), "")
        self.assertEqual(localized_datetime("", "published"), "")

        mock_gettext.assert_not_called()

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_published_today(self, mock_localdate, mock_gettext):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value

        value = self.make_datetime(date(2025, 1, 15))

        result = localized_datetime(value, "published")

        self.assertEqual(result, "Published today at 14:30")

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_published_yesterday(self, mock_localdate, mock_gettext):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value

        value = self.make_datetime(date(2025, 1, 14))

        result = localized_datetime(value, "published")

        self.assertEqual(result, "Published yesterday at 14:30")

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.date_format")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_published_older_date(
        self,
        mock_localdate,
        mock_date_format,
        mock_gettext,
    ):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value
        mock_date_format.return_value = "10/01/2025"

        value = self.make_datetime(date(2025, 1, 10))

        result = localized_datetime(value, "published")

        self.assertEqual(
            result,
            "Published on 10/01/2025 at 14:30",
        )

        mock_date_format.assert_called_once_with(
            date(2025, 1, 10),
            format="DATE_FORMAT",
            use_l10n=True,
        )

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_modified_today(self, mock_localdate, mock_gettext):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value

        value = self.make_datetime(date(2025, 1, 15))

        result = localized_datetime(value, "modified")

        self.assertEqual(result, "modified today at 14:30")

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_modified_yesterday(self, mock_localdate, mock_gettext):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value

        value = self.make_datetime(date(2025, 1, 14))

        result = localized_datetime(value, "modified")

        self.assertEqual(result, "modified yesterday at 14:30")

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.date_format")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_modified_older_date(
        self,
        mock_localdate,
        mock_date_format,
        mock_gettext,
    ):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value
        mock_date_format.return_value = "10/01/2025"

        value = self.make_datetime(date(2025, 1, 10))

        result = localized_datetime(value, "modified")

        self.assertEqual(
            result,
            "modified on 10/01/2025 at 14:30",
        )

    @patch("translations.templatetags.translation_tags.gettext")
    @patch("translations.templatetags.translation_tags.date_format")
    @patch("translations.templatetags.translation_tags.timezone.localdate")
    def test_unknown_action(
        self,
        mock_localdate,
        mock_date_format,
        mock_gettext,
    ):
        mock_localdate.return_value = date(2025, 1, 15)
        mock_gettext.side_effect = lambda value: value
        mock_date_format.return_value = "10/01/2025"

        value = self.make_datetime(date(2025, 1, 10))

        result = localized_datetime(value, "unknown")

        self.assertEqual(result, "10/01/2025 14:30")
