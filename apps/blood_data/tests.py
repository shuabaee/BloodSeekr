from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import services


class GuideTests(TestCase):
    def test_guide_requires_login_then_renders(self):
        self.assertEqual(self.client.get(reverse("blood_data:guide")).status_code, 302)
        self.client.force_login(get_user_model().objects.create_user("g", "g@example.com", "Passw0rd!x"))
        r = self.client.get(reverse("blood_data:guide"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "O-")

    def test_compatibility_is_consistent(self):
        for donor, recipients in services.compatibility_map().items():
            for rec in recipients:
                self.assertIn(donor, services.donors_for(rec))
