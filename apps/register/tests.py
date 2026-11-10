from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):
    def test_register_creates_user(self):
        response = self.client.post(
            reverse("register:register"),
            {
                "first_name": "Joshua",
                "last_name": "Gabison",
                "username": "joshua",
                "email": "joshua@example.com",
                "password": "SafePassword123!",
                "confirm_password": "SafePassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="joshua").exists())

    def test_registration_creates_profile_and_preferences(self):
        self.test_register_creates_user()
        user = User.objects.get(username="joshua")
        self.assertIsNotNone(user.bloodseekr_profile)
        self.assertEqual(user.bloodseekr_settings.match_radius_km,25)

    def test_invalid_email_and_username_are_rejected(self):
        for email, username in [("invalid","new-user"),("valid@example.com","bad username")]:
            response=self.client.post(reverse("register:register"),{"first_name":"Test","last_name":"User","username":username,"email":email,"password":"SafePassword123!","confirm_password":"SafePassword123!"})
            self.assertEqual(response.status_code,200)
        self.assertEqual(User.objects.count(),0)
