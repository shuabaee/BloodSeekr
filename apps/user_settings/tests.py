from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ben", "ben@example.com", "OldPass123!")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse("user_settings:password_change"))
        self.assertEqual(r.status_code, 302)

    def test_change_password_keeps_session(self):
        r = self.client.post(reverse("user_settings:password_change"), {
            "old_password": "OldPass123!", "new_password1": "Fresh789!pass", "new_password2": "Fresh789!pass"})
        self.assertEqual(r.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Fresh789!pass"))
        self.assertEqual(self.client.get(reverse("user_settings:settings")).status_code, 200)
