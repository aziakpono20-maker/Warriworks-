
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User


class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_data = {
            "email": "customer@example.com",
            "username": "customer1",
            "first_name": "Test",
            "last_name": "Customer",
            "password": "StrongPass123!Secure",
        }

        self.artisan_data = {
            "email": "artisan@example.com",
            "username": "artisan1",
            "first_name": "Test",
            "last_name": "Artisan",
            "password": "StrongPass123!Secure",
        }

    def test_customer_registration(self):
        response = self.client.post(
            "/api/auth/register/customer/",
            self.customer_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email="customer@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertTrue(user.check_password(self.customer_data["password"]))

    def test_artisan_registration(self):
        response = self.client.post(
            "/api/auth/register/artisan/",
            self.artisan_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email="artisan@example.com")
        self.assertEqual(user.role, User.Role.ARTISAN)
        self.assertTrue(user.check_password(self.artisan_data["password"]))
        self.assertTrue(hasattr(user, "artisan_profile"))

    def test_public_registration_cannot_create_admin(self):
        data = {
            **self.customer_data,
            "email": "admin@example.com",
            "username": "admin1",
            "role": "admin",
        }

        response = self.client.post(
            "/api/auth/register/customer/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email="admin@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_login_with_valid_credentials(self):
        user = User.objects.create_user(
            email="login@example.com",
            username="loginuser",
            password="StrongPass123!Secure",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "login@example.com",
                "password": "StrongPass123!Secure",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], user.id)

    def test_login_rejects_invalid_password(self):
        User.objects.create_user(
            email="wrongpass@example.com",
            username="wrongpass",
            password="StrongPass123!Secure",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "wrongpass@example.com",
                "password": "IncorrectPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_me(self):
        user = User.objects.create_user(
            email="me@example.com",
            username="meuser",
            password="StrongPass123!Secure",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], user.email)

    def test_logout_requires_authentication(self):
        response = self.client.post("/api/auth/logout/")

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_logout(self):
        user = User.objects.create_user(
            email="logout@example.com",
            username="logoutuser",
            password="StrongPass123!Secure",
        )

        self.client.force_authenticate(user=user)

        response = self.client.post("/api/auth/logout/")

        self.assertEqual(response.status_code, 204)
