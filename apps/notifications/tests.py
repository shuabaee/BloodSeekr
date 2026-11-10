from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class NotificationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("cy", "cy@example.com", "Passw0rd!x")
        self.client.force_login(self.user)

    def test_list_renders_empty(self):
        self.assertEqual(self.client.get(reverse("notifications:list")).status_code, 200)

    def test_mark_all_read_redirects(self):
        r = self.client.post(reverse("notifications:read_all"))
        self.assertEqual(r.status_code, 302)

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("notifications:list")).status_code, 302)
