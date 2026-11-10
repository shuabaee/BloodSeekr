from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="joshua",
            email="joshua@example.com",
            password="SafePassword123!",
        )
        self.client.login(username="joshua", password="SafePassword123!")

    def test_profile_is_created_and_can_be_updated(self):
        response = self.client.post(
            reverse("profile:profile"),
            {
                "first_name": "Joshua",
                "last_name": "Gabison",
                "email": "joshua@example.com",
                "phone_number": "09171234567",
                "blood_type": "O+",
                "date_of_birth": "2000-01-01",
                "location": "Cebu City",
                "available_to_donate": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.blood_type_id, "O+")
        self.assertEqual(profile.location, "Cebu City")
        self.assertTrue(profile.available_to_donate)

    def test_user_cannot_self_verify(self):
        self.client.post(reverse("profile:profile"),{"first_name":"Joshua","last_name":"Gabison","email":"joshua@example.com","is_verified":"on"})
        self.assertFalse(Profile.objects.get(user=self.user).is_verified)

    def test_blood_type_change_clears_verification(self):
        Profile.objects.filter(user=self.user).update(blood_type_id="A+",is_verified=True)
        self.test_profile_is_created_and_can_be_updated()
        self.assertFalse(Profile.objects.get(user=self.user).is_verified)


from django.contrib.auth import get_user_model as _gum
from . import services as _services


class CompletenessTests(TestCase):
    def test_new_user_is_incomplete(self):
        u = _gum().objects.create_user("pat", "", "Passw0rd!x")
        result = _services.completeness(u)
        self.assertFalse(result["complete"])
        self.assertLess(result["percent"], 100)
        self.assertTrue(result["missing"])
