import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import User

from .models import ChatRoom
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    """
        Asynchronous WebSocket consumer that handles chat messages and rooms.

        This consumer manages WebSocket connections for real-time chat functionality, 
        including connecting and disconnecting users, receiving messages from users,
        and broadcasting messages to all users in a chat room.
    """
    async def connect(self):
        """
            Handles the initial WebSocket connection.
            Sets up the room based on the user and receiver IDs, and joins the channel group.
        """
        self.user = self.scope['user']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room = await self.get_room(self.user.id, self.receiver_id)
        self.room_name = await self.parse_uuid(self.room.pk)

        # Adds this connection to the chat room's group for message broadcasting.
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, _):
        """
            Handles WebSocket disconnection.
            Removes the connection from the chat room's group.
        """
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
            Receives a message from the WebSocket, deserializes it, saves it to the database,
            and broadcasts it to the chat room group.
        """
        data = json.loads(text_data)
        message_data = {
            'sender': self.user.pk,
            'room': self.room.pk,
            'content': data['msg']
        }

        serializer = await self.deserialize_message(message_data)

        if not serializer.is_valid():
            print("Serialization error")
            return

        message_obj = await sync_to_async(serializer.save)()
        message_data = await self.serialize_message(message_obj)

        # Broadcasts the message to everyone in the chat room.
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def chat_message(self, event):
        """
            Handles messages sent to the chat room group.
            Sends the message data to the WebSocket.
        """
        message = event['message']

        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def parse_uuid(self, uuid):
        """
            Parses a UUID to a string format suitable for channel layer groups.
        """
        return "chat_{}".format(str(uuid).replace('-', '_'))

    @sync_to_async
    def get_room(self, user_id, receiver_id):
        """
            Retrieves or creates a chat room based on the provided user IDs.
            Ensures that the same room is used regardless of which user is considered user1 or user2.
        """
        user = User.objects.get(pk=user_id)
        other_user = User.objects.get(pk=receiver_id)
        room, _ = ChatRoom.objects.get_or_create(
            user1=min(user, other_user, key=lambda u: u.id),
            user2=max(user, other_user, key=lambda u: u.id),
        )
        return room

    @sync_to_async
    def deserialize_message(self, message_data):
        """
            Deserializes the incoming message data to a Message model instance.
            Validates the data during the process.
        """
        serializer = MessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        return serializer

    @sync_to_async
    def serialize_message(self, message_obj):
        """
            Serializes a Message model instance to JSON format for broadcasting.
        """
        serializer = MessageSerializer(message_obj)
        return serializer.data
