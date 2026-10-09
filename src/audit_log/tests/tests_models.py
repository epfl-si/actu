import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from audit_log.models import GlobalAuditLog, _write_audit_to_file
from audit_log.signals import _get_m2m_field_name

User = get_user_model()


class GlobalAuditLogTests(TestCase):
    def setUp(self):
        self.user_ctype = ContentType.objects.get_for_model(User)

    def test_audit_log_str_representation(self):
        with self.captureOnCommitCallbacks(execute=True):
            user = User.objects.create(username="test_str", sciper="000000")

        log = GlobalAuditLog.objects.filter(object_id=str(user.pk)).first()
        expected_str = (
            f"{log.created_at} - {log.content_type} ({log.object_id})"
        )
        self.assertEqual(str(log), expected_str)

    def test_get_current_state_exception(self):
        user = User.objects.create(username="test_err", sciper="111111")

        with patch(
            "django.db.models.Field.value_from_object",
            side_effect=Exception("Test Boom"),
        ):
            state = user._get_current_state()

        self.assertEqual(state["username"], "Error")

    def test_get_m2m_field_name_fallback(self):
        user = User(username="fallback")
        name = _get_m2m_field_name(user, ContentType)
        self.assertEqual(name, "Unknown relation")

    def test_audit_model_mixin_create_with_m2m(self):
        group = Group.objects.create(name="Admins")

        with self.captureOnCommitCallbacks(execute=True):
            user = User.objects.create(username="hello_user", sciper="222222")
            user.groups.add(group)

        log_create = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Create", object_id=user.pk
        ).first()
        self.assertNotIn("groups", log_create.details)

        log_edit = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit", object_id=user.pk
        ).first()

        self.assertIn("groups", log_edit.details.get("changes", {}))

    def test_audit_model_mixin_m2m_changed_normal(self):
        user = User.objects.create(username="m2m_normal", sciper="333333")
        group = Group.objects.create(name="Editors")

        with self.captureOnCommitCallbacks(execute=True):
            user.groups.add(group)

        log_edit = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit", object_id=user.pk
        ).last()

        self.assertIsNotNone(log_edit)
        self.assertIn("groups", log_edit.details.get("changes", {}))

    def test_audit_m2m_changed_reverse(self):
        user = User.objects.create(username="m2m_reverse", sciper="444444")
        group = Group.objects.create(name="SuperAdmins")

        with self.captureOnCommitCallbacks(execute=True):
            group.user_set.add(user)

        log_edit = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit", object_id=user.pk
        ).last()

        self.assertIsNotNone(log_edit)
        self.assertIn("groups", log_edit.details.get("changes", {}))

    def test_audit_model_mixin_delete(self):
        user = User.objects.create(username="delete_test", sciper="555555")
        user_id = user.pk
        user.delete()

        log_delete = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Delete", object_id=user_id
        ).first()

        self.assertIsNotNone(log_delete)

    def test_audit_model_bulk_create(self):
        users = [
            User(username=f"bulk_c_{i}", sciper=f"66666{i}") for i in range(3)
        ]
        User.objects.bulk_create(users)

        logs = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Create"
        )

        self.assertEqual(logs.count(), 3)

        first_log_details = logs.first().details

        self.assertIsInstance(first_log_details["username"], str)
        self.assertTrue(first_log_details["username"].startswith("bulk_c_"))

    def test_audit_model_bulk_update(self):
        u1 = User.objects.create(username="old_u1", sciper="777771")
        u2 = User.objects.create(username="old_u2", sciper="777772")

        u1.sciper = "888881"
        u2.sciper = "888882"
        User.objects.bulk_update([u1, u2], ["sciper"])

        logs = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit"
        )
        self.assertEqual(logs.count(), 2)

        changes = logs[1].details.get("changes", {})
        self.assertEqual(len(changes["sciper"]), 2)
        self.assertEqual(changes["sciper"][0], "777771")
        self.assertEqual(changes["sciper"][1], "888881")

    def test_audit_model_bulk_delete(self):
        User.objects.create(username="del_1", sciper="999991")
        User.objects.create(username="del_2", sciper="999992")

        User.objects.filter(username__startswith="del_").delete()

        logs = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Delete"
        )
        self.assertTrue(logs.count() >= 2)

    def test_user_model_create_user(self):
        with self.captureOnCommitCallbacks(execute=True):
            new_user = User.objects.create_user(
                username="agent",
                password="supersecretpassword",
                sciper="12341234",
            )

        log = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype,
            action="Create",
            object_id=str(new_user.pk),
        ).first()

        self.assertIsNotNone(log)
        self.assertEqual(log.details["sciper"], "12341234")

    @patch("audit_log.models.logger.info")
    def test_write_audit_to_file_edge_cases(self, mock_logger):
        with self.captureOnCommitCallbacks(execute=True):
            User.objects.create(username="opdo_user", sciper="777888")

        self.assertTrue(mock_logger.called)

        log_json_string = mock_logger.call_args[0][0]
        log_data = json.loads(log_json_string)
        payload = json.loads(log_data["payload"])

        self.assertIn("@timestamp", log_data)
        self.assertEqual(log_data["crudt"], "c")
        self.assertEqual(log_data["source"], "actu-opdo")
        self.assertEqual(log_data["handler_id"], "System")
        self.assertEqual(log_data["handled_id"], "system-background-task")
        self.assertIn("object_name", payload)
        self.assertEqual(payload["details"]["username"], "opdo_user")

    @patch("audit_log.models.logger.info")
    def test_write_audit_to_file_cleaning_and_lazy_text(self, mock_logger):
        mock_log = Mock()
        mock_log.content_type = "Thematics | Thematic"
        mock_log.object_id = "42"
        mock_log.object_repr = "Lazy Title"
        mock_log.action = "Delete"
        mock_log.user = _("System")
        mock_log.details = {"foo": "bar"}
        mock_log.created_at = None

        _write_audit_to_file(mock_log)

        log_json_string = mock_logger.call_args[0][0]
        log_data = json.loads(log_json_string)
        payload = json.loads(log_data["payload"])

        self.assertEqual(log_data["crudt"], "d")
        self.assertEqual(log_data["handled_id"], "system-background-task")
        self.assertEqual(log_data["handler_id"], "System")
        self.assertEqual(payload["object_name"], "Lazy Title")
