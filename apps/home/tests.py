from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.profile.models import Profile


class HomeViewTests(TestCase):
    def test_home_requires_login_and_displays_profile_data(self):
        response = self.client.get(reverse("home:home"))
        self.assertRedirects(
            response,
            f"{reverse('login:login')}?next={reverse('home:home')}",
        )

        user = User.objects.create_user(
            username="joshua",
            password="SafePassword123!",
        )
        Profile.objects.filter(user=user).update(blood_type_id="O+", location="Cebu City")
        self.client.login(username="joshua", password="SafePassword123!")

        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "O+")
        self.assertContains(response, "Cebu City")
