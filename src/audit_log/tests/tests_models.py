from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from audit_log.models import GlobalAuditLog
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
        self.assertIn("groups", log_edit.details)

    def test_audit_model_mixin_m2m_changed_normal(self):
        user = User.objects.create(username="m2m_normal", sciper="333333")
        group = Group.objects.create(name="Editors")

        with self.captureOnCommitCallbacks(execute=True):
            user.groups.add(group)

        log_edit = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit", object_id=user.pk
        ).last()

        self.assertIsNotNone(log_edit)
        self.assertIn("groups", log_edit.details)

    def test_audit_m2m_changed_reverse(self):
        user = User.objects.create(username="m2m_reverse", sciper="444444")
        group = Group.objects.create(name="SuperAdmins")

        with self.captureOnCommitCallbacks(execute=True):
            group.user_set.add(user)

        log_edit = GlobalAuditLog.objects.filter(
            content_type=self.user_ctype, action="Edit", object_id=user.pk
        ).last()

        self.assertIsNotNone(log_edit)
        self.assertIn("groups", log_edit.details)

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
        self.assertIsInstance(first_log_details["username"], list)
        self.assertEqual(len(first_log_details["username"]), 2)
        self.assertEqual(first_log_details["username"][0], "")

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

        first_log_details = logs[1].details
        self.assertEqual(len(first_log_details["sciper"]), 2)
        self.assertEqual(first_log_details["sciper"][0], "777771")
        self.assertEqual(first_log_details["sciper"][1], "888881")

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
        self.assertEqual(log.details["sciper"][1], "12341234")
