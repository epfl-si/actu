from django.test import TestCase
from django.urls import reverse


class APIInfrastructureTests(TestCase):

    def test_docs_url(self):
        url = reverse("api-docs", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schema_returns_openapi_document(self):
        url = reverse("schema", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("openapi: 3", content)

    def test_invalid_api_version(self):
        response = self.client.get("/api/v0/schema/")
        self.assertEqual(response.status_code, 404)
