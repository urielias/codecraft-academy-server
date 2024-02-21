from .models import User
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class AuthenticationTests(TestCase):
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

    def test_signup_success(self):
        response = self.client.post(
            self.signup_url, self.signup_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_signup_invalid_data(self):
        invalid_data = self.signup_data.copy()
        invalid_data['email'] = 'invalid'
        response = self.client.post(
            self.signup_url, invalid_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_login_success(self):
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.login_data['username'],
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, 401)


class UserFetchingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_students_url = reverse('list_students')
        self.list_teachers_url = reverse('list_teachers')
        self.users = []

        self.users_data = [{
            'first_name': 'User1',
            'last_name': 'Last1',
            'username': 'user1',
            'password': 'password123',
            'email': 'user1@email.com',
            'user_type': 'STUDENT',
        }, {
            'first_name': 'User2',
            'last_name': 'Last2',
            'username': 'user2',
            'password': 'password123',
            'email': 'user2@email.com',
            'user_type': 'STUDENT',
        }, {
            'first_name': 'User3',
            'last_name': 'Last3',
            'username': 'user3',
            'password': 'password123',
            'email': 'user3@email.com',
            'user_type': 'TEACHER',
        }]

        for user in self.users_data:
            temp_user = User.objects.create(**user)
            temp_user.set_password(user['password'])
            temp_user.save()
            self.users.append(temp_user)

    def test_get_students_success(self):
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_students_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_students_search_success(self):
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_students_url, {
                                   'search': 'Last2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_teachers_success(self):
        auth_user = self.users[2]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_teachers_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_teachers_unauth(self):
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_teachers_url, format='json')
        self.assertEqual(response.status_code, 403)
