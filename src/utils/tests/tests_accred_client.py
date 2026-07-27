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
        self.assertEqual(self.client.search_persons_by_right("Iivo"), [])
        self.assertIsNone(self.client.get_person_details("99999996"))

    @patch("requests.get", side_effect=requests.RequestException("Down"))
    def test_handles_network_crashes(self, mock_get):
        """Both methods must catch network exceptions gracefully."""
        self.assertEqual(self.client.search_persons_by_right("Iivo"), [])
        self.assertIsNone(self.client.get_person_details("99999996"))

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
                        "sciper": 99999996,
                        "firstname": "Iivo",
                        "lastname": "Niskanen",
                    }
                },
                {
                    "person": {
                        "id": 99999997,
                        "firstname": "Kerttu",
                        "lastname": "Niskanen",
                    }
                },
                {
                    "person": {
                        "sciper": 99999998,
                        "firstname": "Alberto",
                        "lastname": "Tomba",
                    }
                },
                {"person": {"firstname": "Issa", "lastname": "Laborde"}},
            ]
        }
        mock_get.return_value = mock_response

        res_name = self.client.search_persons_by_right("Iivo niskanen")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0]["sciper"], "99999996")

        res_sciper = self.client.search_persons_by_right("99999997")
        self.assertEqual(len(res_sciper), 1)
        self.assertEqual(res_sciper[0]["sciper"], "99999997")

    @patch("requests.get")
    def test_get_details_username_extraction(self, mock_get):
        """Tests the 3 fallback strategies for username extraction."""
        mock_get.side_effect = [
            MagicMock(json=lambda: {"username": "iniskanen"}),
            MagicMock(json=lambda: {"account": {"username": "atomba"}}),
            MagicMock(
                json=lambda: {"firstname": "Issa", "lastname": "Laborde"}
            ),
        ]

        res_root = self.client.get_person_details("99999996")
        self.assertEqual(res_root["username"], "iniskanen")

        res_nested = self.client.get_person_details("99999998")
        self.assertEqual(res_nested["username"], "atomba")
