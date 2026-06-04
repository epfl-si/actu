from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase

from ..mail import ToAdminEmailBackend


class ToAdminEmailBackendTestCase(TestCase):

    def setUp(self):
        self.original_admins = settings.ADMINS

        settings.ADMINS = [
            ("Alberto Tomba", "alberto.tomba@epfl.ch"),
            ("livo Niskanen", "livo.niskanen@epfl.ch"),
        ]

        self.backend = ToAdminEmailBackend()

    def tearDown(self):
        settings.ADMINS = self.original_admins

    def test_email_backend_initialization(self):
        self.assertEqual(len(self.backend.admin_emails), 2)
        self.assertIn("alberto.tomba@epfl.ch", self.backend.admin_emails)

    def test_email_backend_initialization_with_invalid_admins(self):
        settings.ADMINS = []
        self.backend = ToAdminEmailBackend()
        self.assertEqual(len(self.backend.admin_emails), 0)

    def test_email_backend_send_messages_empty_email(self):
        result = self.backend.send_messages([])
        self.assertEqual(result, 0)

    @patch("django.core.mail.backends.smtp.EmailBackend.send_messages")
    def test_email_backend_send_messages(self, mock_send_messages):
        email = mail.EmailMessage(
            subject="Slalom - Gold Winner",
            body="Calgary 1988",
            from_email=settings.SERVER_EMAIL,
            to=["johannes.klaebo@epfl.ch", "bjorn.daehlie@epfl.ch"],
        )

        # Mock the send_messages method to return 1
        mock_send_messages.return_value = 1

        result = self.backend.send_messages([email])
        self.assertEqual(result, 1)

        self.assertEqual(
            email.subject,
            "Slalom - Gold Winner (original recipients: "
            "johannes.klaebo@epfl.ch;bjorn.daehlie@epfl.ch)",
        )
