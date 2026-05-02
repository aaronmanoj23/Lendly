from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.test import TestCase

from users.adapters import EduOnlyAdapter

User = get_user_model()


class UserTests(TestCase):
    def test_edu_only(self):
        adapter = EduOnlyAdapter()
        with self.assertRaises(ValidationError):
            adapter.clean_email("bad@gmail.com")
        self.assertEqual(adapter.clean_email("ok@cpp.edu"), "ok@cpp.edu")

    def test_create_user(self):
        u = User.objects.create_user(email="a@cpp.edu", password="pw12345!")
        self.assertEqual(str(u), "a@cpp.edu")
        self.assertTrue(u.check_password("pw12345!"))
