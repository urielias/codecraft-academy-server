from rest_framework import serializers

from users.models import User

from .models import Message, ChatRoom


class MessageSerializer(serializers.ModelSerializer):
    """
        Serializer for the Message model.

        Attributes:
            sender (PrimaryKeyRelatedField): A field to serialize the sender of the message by their primary key.
                                            This field is write-only to ensure that the sender's ID is not included
                                            when reading messages.
            room (PrimaryKeyRelatedField): A field to serialize the chat room associated with the message.
                                            Uses a custom field for the primary key to handle UUID fields in a verbose format.
                                            This field is write-only.

        The serializer includes the message content, associated room, timestamp, and sender ID.
    """
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    room = serializers.PrimaryKeyRelatedField(
        queryset=ChatRoom.objects.all(),
        pk_field=serializers.UUIDField(format='hex_verbose'),
        write_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'content', 'room', 'timestamp', 'sender']


class ChatRoomSerialzer(serializers.ModelSerializer):
    """
        Serializer for the ChatRoom model.

        Attributes:
            messages (SerializerMethodField): A dynamic field that serializes all messages associated with the chat room,
                                                ordered by their timestamp.
            other_user (SerializerMethodField): A dynamic field that determines and serializes the "other" user in the chat room
                                                relative to the request user.

        This serializer is designed to provide a comprehensive view of a chat room, including all associated messages
        and the identity of the other participant in the chat.
    """
    messages = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'created_at', 'other_user', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('timestamp')
        return MessageSerializer(messages, many=True, context={'request': self.context.get('request')}).data

    def get_other_user(self, obj):
        request = self.context.get('request')
        if obj.user1 == request.user:
            return str(obj.user2)
        else:
            return str(obj.user1)
