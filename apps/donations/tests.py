from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DonationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("di", "di@example.com", "Passw0rd!x")
        self.client.force_login(self.user)

    def test_list_tabs_render(self):
        for role in ("all", "donor", "requester"):
            r = self.client.get(reverse("donations:list"), {"role": role})
            self.assertEqual(r.status_code, 200)

    def test_export_csv(self):
        r = self.client.get(reverse("donations:export"))
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r["Content-Type"])

    def test_export_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("donations:export")).status_code, 302)
