from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from .models import User, UserProfile
from rest_framework.test import APIClient


class UserAccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

        self.signup_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'username': 'jsmith',
            'password': 'password123',
            'email': 'jsmith@email.com',
        }

        login_user = {
            'username': 'jjohnson',
            'password': 'password123',
            'email': 'jjohnson@email.com',
        }

        login_user_profile = {
            'first_name': 'James',
            'last_name': 'Johnson',
        }

        self.login_data = {
            'username': 'jjohnson',
            'password': 'password123',
        }

        self.user = User.objects.create(**login_user)
        self.user.set_password(login_user["password"])
        self.user.save()
        self.profile = UserProfile.objects.create(
            user=self.user, **login_user_profile)

    def test_signup_success(self):
        response = self.client.post(
            self.signup_url, self.signup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_signup_invalid_data(self):
        invalid_data = self.signup_data.copy()
        invalid_data['email'] = 'invalid'
        response = self.client.post(
            self.signup_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.login_data['username'],
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
