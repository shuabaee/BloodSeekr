from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", "ana@example.com", "OldPass123!")

    def test_reset_request_sends_email(self):
        r = self.client.post(reverse("login:password_reset"), {"email": "ana@example.com"})
        self.assertRedirects(r, reverse("login:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)

    def test_unknown_email_does_not_reveal_account(self):
        r = self.client.post(reverse("login:password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(r, reverse("login:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_sets_new_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("login:password_reset_confirm", args=[uid, "set-password"])
        token = default_token_generator.make_token(self.user)
        r = self.client.get(reverse("login:password_reset_confirm", args=[uid, token]))
        self.assertEqual(r.status_code, 302)
        r = self.client.post(r["Location"], {"new_password1": "BrandNew456!x", "new_password2": "BrandNew456!x"})
        self.assertRedirects(r, reverse("login:password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew456!x"))
