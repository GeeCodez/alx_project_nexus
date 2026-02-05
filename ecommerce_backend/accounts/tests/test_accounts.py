from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class TestAccounts(APITestCase):

    def setUp(self):
        # Creating a user for login/profile tests
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            phone_number="+15555555555",
            password="strongpassword"
        )
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")

    def test_register_user_success(self):
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_missing_fields(self):
        data={
            "username": "incompleteuser",
            "password": "password123"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="incompleteuser").exists())
    
    def test_login_with_username(self):
        data = {"identifier": "testuser", "password": "strongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data) #type: ignore
        self.assertIn("refresh", response.data) #type: ignore

    def test_login_with_email(self):
        data = {"identifier": "test@example.com", "password": "strongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_phone(self):
        data = {"identifier": "+15555555555", "password": "strongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        data = {"identifier": "wronguser", "password": "wrongpass"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_authenticated(self):
        # Get token first
        login_data = {"identifier": "testuser", "password": "strongpassword"}
        login_response = self.client.post(self.login_url, login_data)
        access = login_response.data["access"] #type: ignore

        # Call /me/ with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}") #type: ignore
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser") #type: ignore

    def test_me_endpoint_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)