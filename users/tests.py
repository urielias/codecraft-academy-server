from .models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class AuthenticationTests(APITestCase):
    """
        Test suite for user authentication endpoints including signup, login, and logout.

        This class tests the functionality of creating new user accounts, authenticating
        users with correct credentials, and logging out users by invalidating tokens.
    """

    def setUp(self):
        """
            Prepares data and endpoints for testing authentication processes.
        """
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

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
        """
            Verifies that a new user can sign up and receives a token upon successful registration.
        """
        response = self.client.post(
            self.signup_url, self.signup_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_signup_invalid_data(self):
        """
            Ensures that the signup process validates data correctly and rejects invalid inputs.
        """
        invalid_data = self.signup_data.copy()
        invalid_data['email'] = 'invalid'
        response = self.client.post(
            self.signup_url, invalid_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_login_success(self):
        """
            Tests that a user can log in with valid credentials and receives a token.
        """
        response = self.client.post(
            self.login_url, self.login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        """
            Confirms that the login process rejects incorrect credentials.
        """
        response = self.client.post(self.login_url, {
            'username': self.login_data['username'],
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_logout_success(self):
        """
            Checks that a user can log out, effectively invalidating their authentication token.
        """
        response = self.client.post(self.login_url, self.login_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + response.data['token'])
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(Token.DoesNotExist,
                          Token.objects.get, user=self.user)


class UserFetchingTests(APITestCase):
    """
        Test suite for fetching lists of users, specifically students and teachers, from the application.

        Includes tests for accessing these lists with proper authorization and ensuring that search
        functionality filters the user lists correctly.
    """

    def setUp(self):
        """
            Sets up user instances and authentication tokens for testing user list fetching.
        """
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
        """
            Validates successful retrieval of a list of students when requested by an authenticated user.
        """
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_students_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_students_search_success(self):
        """
            Tests the search functionality on the student list endpoint to ensure correct filtering.
        """
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_students_url, {
                                   'search': 'Last2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_teachers_success(self):
        """
            Verifies that the list of teachers can be successfully retrieved by an authenticated user.
        """
        auth_user = self.users[2]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(self.list_teachers_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_teachers_unauth(self):
        """
            Ensures that unauthorized requests are properly rejected from accessing teacher data.
        """
        auth_user = self.users[0]
        token = Token.objects.create(user=auth_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.list_teachers_url, format='json')
        self.assertEqual(response.status_code, 403)
