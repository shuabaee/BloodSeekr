from django.test import TestCase



class ErrorPageTests(TestCase):
    def test_404_is_friendly(self):
        r = self.client.get("/definitely-not-here/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "BloodSeekr", status_code=404)
