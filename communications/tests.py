import json
from uuid import uuid4

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter

from users.models import User

from .models import ChatRoom, Message
from .routing import websocket_urlpatterns
from .token_auth_middleware import TokenAuthMiddleware


class ChatTests(TestCase):
    """
        Test suite for chat functionality in a Django Channels application.

        This class tests the WebSocket communication for sending and receiving messages
        in a chat application, ensuring that the token authentication middleware and message
        handling are working as expected.
    """

    def setUp(self):
        """
            Set up the environment for chat tests.

            Creates two users and generates a token for one of them to simulate authenticated
            WebSocket connections. Also, prepares a sample message payload to be used in the tests.
        """
        self.user1 = User.objects.create(
            username='student', password='pass', first_name='User1', last_name='student', user_type=User.UserType.STUDENT)
        self.token = Token.objects.create(user=self.user1)
        self.user2 = User.objects.create(
            username='teacher', password='pass', first_name='User2', last_name='teacher', user_type=User.UserType.TEACHER)

        self.message = {'msg': 'This is my message'}

    async def test_websocket_message(self):
        """
            Test the WebSocket message exchange between users in the chat.

            This test ensures that a WebSocket connection can be established using token
            authentication, and verifies that messages sent through the WebSocket are received
            and correctly echoed back, demonstrating successful message exchange.
        """
        receiver_id = self.user2.pk

        # Set up the application with WebSocket and authentication middleware.
        app = ProtocolTypeRouter({
            "websocket": TokenAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                )
            ),
        })

        # Create a WebSocket communicator with authentication token and connect to it.
        communicator = WebsocketCommunicator(
            app, 'ws/chat/{}/?token={}'.format(receiver_id, self.token))
        connected, _ = await communicator.connect()

        # Ensure the WebSocket connection was successfully established.
        self.assertTrue(connected)

        # Send and receive message through the WebSocket.
        await communicator.send_to(text_data=json.dumps(self.message))
        response = await communicator.receive_from()
        data = json.loads(response)

        # Verify the received message matches what was sent and disconnect the communicator.
        self.assertEqual(data['content'], self.message['msg'])
        await communicator.disconnect()


class ChatHistoryTests(APITestCase):
    """
        Test suite for the chat history retrieval feature.

        This class tests the API endpoint responsible for retrieving the chat history of a specific chat room,
        ensuring that the endpoint behaves correctly under various circumstances including successful data retrieval,
        authentication and permission checks, and handling non-existing resources.
    """

    def setUp(self):
        """
            Sets up the necessary data for the tests.

            Creates three users and a chat room between the first two users, then populates the chat room with messages.
            It also constructs the URL for accessing the chat history endpoint.
        """
        self.user1 = User.objects.create_user(
            'user1', 'user1@example.com', 'password123')
        self.user2 = User.objects.create_user(
            'user2', 'user2@example.com', 'password123')
        self.user3 = User.objects.create_user(
            'user3', 'user3@example.com', 'password123')

        self.chat_room = ChatRoom.objects.create(
            user1=self.user1, user2=self.user2)

        Message.objects.create(
            sender=self.user1, room=self.chat_room, content="Hello, World!")
        Message.objects.create(
            sender=self.user2, room=self.chat_room, content="Hi there!")

        self.url = reverse('chat_history', kwargs={
                           'room_id': self.chat_room.id})

    def test_retrieve_chat_history_success(self):
        """
            Tests successful retrieval of chat history for a member of the chat room.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_authentication_required(self):
        """
            Tests that authentication is required to access the chat history.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_permission_check_member_of_room(self):
        """
            Tests that only members of the chat room can retrieve its history.
        """
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_chat_room_not_found(self):
        """
            Tests handling of requests for non-existing chat rooms.
        """
        self.client.force_authenticate(user=self.user1)
        non_existing_id = uuid4()
        url = reverse('chat_history', kwargs={'room_id': non_existing_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
