import unittest
from django.test import Client
from rest_framework import status
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'test@gmail.com'
        self.password = 'testpassword'

        # Create a test user
        self.user = User.objects.create_user(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.login_url = '/login/'  # Update with your actual login endpoint

    def test_login_success(self):
        # Send POST request to login API
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        }, content_type='application/json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains a JWT token
        response_data = json.loads(response.content)
        self.assertIn('access', response_data["data"])
        self.assertIn('refresh', response_data["data"])
        self.assertIsInstance(response_data["data"]["access"], str)

    def test_login_invalid_credentials(self):
        # Send POST request with invalid credentials
        response = self.client.post(self.login_url, {
            'email': 'wronguser@gmail.com',
            'password': 'wrongpassword'
        }, content_type='application/json')

        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        # Clean up after tests
        User.objects.all().delete()
