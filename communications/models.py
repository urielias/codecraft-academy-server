from uuid import uuid4

from django.db import models

from users.models import User


class StatusUpdate(models.Model):
    """
        A model representing a status update by a user.

        Attributes:
            user (ForeignKey): A reference to the User who posted the status update.
            content (TextField): The content of the status update.
            posted_at (DateTimeField): The date and time when the status update was posted.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='status_updates')
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)


class ChatRoom(models.Model):
    """
        A model representing a chat room for two users.

        Attributes:
            id (UUIDField): The unique identifier for the chat room. Automatically generated.
            user1 (ForeignKey): A reference to the first User in the chat.
            user2 (ForeignKey): A reference to the second User in the chat.
            created_at (DateTimeField): The date and time when the chat room was created.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user1 = models.ForeignKey(
        User, related_name='chats_started', on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, related_name='chats_invited', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Returns a human-readable string representation of the ChatRoom instance.
            Shows the 2 users involved in the chat room.
            Used mainly for debugging
        """
        return "Chat between {} and {}".format(self.user1, self.user2)

    def is_member(self, user: User):
        """
            Determines if the specified user is a member of the chat room.

            Args:
                user (User): The user to check for membership.

            Returns:
                bool: True if the user is either user1 or user2 in the chat room; False otherwise.
        """
        return user == self.user1 or user == self.user2


class Message(models.Model):
    """
        A model representing a message in a chat room.

        Attributes:
            sender (ForeignKey): A reference to the User who sent the message.
            room (ForeignKey): A reference to the ChatRoom where the message was sent.
            content (TextField): The content of the message.
            timestamp (DateTimeField): The date and time when the message was sent.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(
        ChatRoom, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Returns a human-readable string representation of the Message instance.
            Shows the sender and timestamp of the message
            Used mainly for debugging
        """
        return "{} at {}".format(self.sender, self.timestamp)
