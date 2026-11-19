from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_page_links_to_login(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("login"))
        self.assertContains(response, "Create Your Account")

    def test_registration_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "Strong-test-pass-928!",
                "password2": "Strong-test-pass-928!",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_registration_rejects_duplicate_username(self):
        User.objects.create_user(username="existing", password="Strong-test-pass-928!")

        response = self.client.post(
            reverse("register"),
            {
                "username": "existing",
                "email": "another@example.com",
                "password1": "Strong-test-pass-928!",
                "password2": "Strong-test-pass-928!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())


class AuthenticationTests(TestCase):
    def setUp(self):
        self.password = "Strong-test-pass-928!"
        self.user = User.objects.create_user(
            username="sepehr",
            email="sepehr@example.com",
            password=self.password,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_get_does_not_log_user_out(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("dashboard"))
        self.assertIn("_auth_user_id", self.client.session)
