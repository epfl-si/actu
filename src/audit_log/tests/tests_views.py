from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse

from audit_log.models import GlobalAuditLog

User = get_user_model()


class GlobalHistoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="password",
            email="admin@test.com",
            sciper="123223",
        )
        self.normal_user = User.objects.create_user(
            username="user",
            password="password",
            email="user@test.com",
            sciper="123456",
        )

        self.url = reverse("global_history")
        self.content_type = ContentType.objects.get_for_model(User)

        GlobalAuditLog.objects.create(
            content_type=self.content_type,
            object_id="1",
            object_repr="test",
            action="Create",
            user="admin",
            details={"title": ["", "Accueil"]},
        )
        GlobalAuditLog.objects.create(
            content_type=self.content_type,
            object_id="2",
            object_repr="news-1",
            action="Edit",
            user="System",
            details={"status": ["Draft", "Published"]},
        )

    def test_access_forbidden_for_normal_user(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_forbidden_for_inactive_superuser(self):
        self.superuser.is_active = False
        self.superuser.save()
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_filters_with_dates_and_type(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            self.url,
            {
                "type": "user",
                "from": "2026-08-01",
                "to": "2026-08-31",
            },
        )
        self.assertEqual(response.status_code, 200)

        response_invalid = self.client.get(
            self.url, {"from": "ceci-nest-pas-une-date"}
        )
        self.assertEqual(response_invalid.status_code, 200)

    def test_format_single_log_valid_field(self):
        self.client.force_login(self.superuser)
        GlobalAuditLog.objects.create(
            content_type=self.content_type,
            object_id="1",
            action="Edit",
            details={"username": ["old", "new"]},
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_format_single_log_list_fallback(self):
        self.client.force_login(self.superuser)
        GlobalAuditLog.objects.create(
            content_type=self.content_type,
            object_id="2",
            action="Edit",
            details=["ceci", "est", "une", "liste"],
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_format_single_log_malformed_json(self):
        self.client.force_login(self.superuser)
        GlobalAuditLog.objects.create(
            content_type=self.content_type,
            object_id="3",
            action="Edit",
            details="{json_cassé: oui",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_allowed_for_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("timeline", response.context)
        self.assertEqual(len(response.context["timeline"]), 2)
        self.assertIn("active_types", response.context)
        self.assertIn("active_users", response.context)

    def test_filter_by_action(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url, {"action": "Create"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["timeline"]), 1)
        self.assertEqual(response.context["timeline"][0]["action"], "Create")

    def test_filter_by_search_keyword(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url, {"search": "News"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["timeline"]), 1)
        self.assertEqual(response.context["timeline"][0]["subject"], "news-1")

    def test_filter_by_user(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url, {"user": "System"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["timeline"]), 1)
        self.assertEqual(response.context["timeline"][0]["user"], "System")

    def test_pagination(self):
        logs = [
            GlobalAuditLog(
                content_type=self.content_type,
                object_id=str(i),
                object_repr=f"Item {i}",
                action="Edit",
                user="admin",
                details={},
            )
            for i in range(1, 45)
        ]
        GlobalAuditLog.objects.bulk_create(logs)

        self.client.force_login(self.superuser)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context["timeline"]), 30)
        self.assertTrue(response.context["page_obj"].has_next())

        response_page_2 = self.client.get(self.url, {"page": "2"})
        self.assertEqual(len(response_page_2.context["timeline"]), 16)
