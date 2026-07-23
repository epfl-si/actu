from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase, override_settings

from utils.accred_client import AccredServiceClient


@override_settings(
    ACTU_API_USERNAME="test_user",
    ACTU_API_PASSWORD="test_password",
    ACTU_API_BASE_URL="https://api.example.com",
    ACTU_API_RIGHT_ID="123",
)
class TestAccredServiceClient(TestCase):
    def setUp(self):
        self.client = AccredServiceClient()

    def test_aborts_without_credentials(self):
        """Both methods must abort early if credentials are missing."""
        self.client.username = None
        self.assertEqual(self.client.search_persons_by_right("Alice"), [])
        self.assertIsNone(self.client.get_person_details("111111"))

    @patch("requests.get", side_effect=requests.RequestException("Down"))
    def test_handles_network_crashes(self, mock_get):
        """Both methods must catch network exceptions gracefully."""
        self.assertEqual(self.client.search_persons_by_right("Alice"), [])
        self.assertIsNone(self.client.get_person_details("111111"))

    def test_search_empty_query(self):
        """Search must abort if query is empty."""
        self.assertEqual(self.client.search_persons_by_right("   "), [])

    @patch("requests.get")
    def test_search_filtering_logic(self, mock_get):
        """Tests search filtering (SCIPER vs Name) and duplicates."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "authorizations": [
                {
                    "person": {
                        "sciper": 111111,
                        "firstname": "Alice",
                        "lastname": "Dupont",
                    }
                },
                {
                    "person": {
                        "id": 111110,
                        "firstname": "Ali",
                        "lastname": "Dupont",
                    }
                },
                {
                    "person": {
                        "sciper": 222222,
                        "firstname": "Bob",
                        "lastname": "Martin",
                    }
                },
                {"person": {"firstname": "Charlie"}},
            ]
        }
        mock_get.return_value = mock_response

        res_name = self.client.search_persons_by_right("alice dupont")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0]["sciper"], "111111")

        res_sciper = self.client.search_persons_by_right("222222")
        self.assertEqual(len(res_sciper), 1)
        self.assertEqual(res_sciper[0]["sciper"], "222222")

    @patch("requests.get")
    def test_get_details_username_extraction(self, mock_get):
        """Tests the 3 fallback strategies for username extraction."""
        mock_get.side_effect = [
            MagicMock(json=lambda: {"username": "adupont"}),
            MagicMock(json=lambda: {"account": {"username": "bmartin"}}),
            MagicMock(json=lambda: {"firstname": "Charlie"}),
        ]

        res_root = self.client.get_person_details("111111")
        self.assertEqual(res_root["username"], "adupont")

        res_nested = self.client.get_person_details("222222")
        self.assertEqual(res_nested["username"], "bmartin")

        res_fallback = self.client.get_person_details("333333")
        self.assertEqual(res_fallback["username"], "333333")
