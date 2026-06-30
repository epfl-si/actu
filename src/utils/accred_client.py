import logging

import requests
from django.conf import settings

logger = logging.getLogger("django")


class AccredServiceClient:
    REQUEST_TIMEOUT = 10

    def __init__(self):
        self.username = settings.ACTU_API_USERNAME
        self.password = settings.ACTU_API_PASSWORD
        self.api_url = settings.ACTU_API_BASE_URL
        self.right_id = settings.ACTU_API_RIGHT_ID

    def search_persons_by_right(self, search_query):
        if not self.username or not self.password:
            logger.error("[AccredServiceClient] Missing service credentials.")
            return []

        clean_query = search_query.strip()
        if not clean_query:
            return []

        url = f"{self.api_url}/v1/authorizations"
        query_parts = clean_query.split()
        api_search_term = max(query_parts, key=len)

        params = {
            "type": "right",
            "authid": self.right_id,
            "alldata": 1,
            "searchperson": api_search_term,
        }

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                params=params,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            authorizations_list = data.get("authorizations", [])

            return self._filter_persons(
                authorizations_list, clean_query, query_parts
            )

        except requests.RequestException as e:
            logger.error(
                "[AccredServiceClient] Search failed "
                f"on v1/authorizations: {e}"
            )
            return []

    def _filter_persons(self, authorizations_list, clean_query, query_parts):
        unique_persons = {}

        for auth in authorizations_list:
            person_data = auth.get("person", {})
            sciper = person_data.get("sciper") or person_data.get("id")

            if not sciper:
                continue

            sciper_str = str(sciper)
            first_name = person_data.get("firstname", "")
            last_name = person_data.get("lastname", "")
            full_name = f"{first_name} {last_name}".lower()

            match = sciper_str == clean_query or all(
                part.lower() in full_name for part in query_parts
            )

            if match and sciper_str not in unique_persons:
                unique_persons[sciper_str] = {
                    "sciper": sciper_str,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": person_data.get("email", ""),
                    "displayName": f"{first_name} {last_name} ({sciper_str})",
                }

        return list(unique_persons.values())

    def get_person_details(self, sciper):
        if not self.username or not self.password:
            logger.error("[AccredServiceClient] Missing service credentials.")
            return None

        url = f"{self.api_url}/v1/persons/{sciper}"

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            person_data = response.json()

            username = person_data.get("username")
            if not username:
                account_data = person_data.get("account", {})
                username = account_data.get("username", str(sciper))

            return {
                "sciper": str(sciper),
                "username": username,
                "first_name": person_data.get("firstname", ""),
                "last_name": person_data.get("lastname", ""),
                "email": person_data.get("email", ""),
            }

        except requests.RequestException as e:
            logger.error(
                "[AccredServiceClient] Failed to fetch details "
                f"for SCIPER {sciper}: {e}"
            )
            return None
