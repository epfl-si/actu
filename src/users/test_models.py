from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user_with_sciper(self):
        user = User.objects.create_user(username="test", sciper="99999999")
        self.assertEqual(user.username, "test")
        self.assertEqual(user.sciper, "99999999")

    def test_sciper_is_unique(self):
        User.objects.create_user(username="test", sciper="99999999")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="test2", sciper="99999999")
