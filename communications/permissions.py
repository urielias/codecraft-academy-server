from rest_framework.permissions import BasePermission

from .models import ChatRoom


class IsMemberOfRoom(BasePermission):
    """
        Custom permission to only allow members of a chat room to interact with it.

        This permission checks if the current request's user is a member of the room
        by calling the `is_member` method of the room object. It's designed to be used
        in views that operate on individual room instances to ensure that a user cannot
        access or modify rooms they are not a part of.
    """

    def has_object_permission(self, request, _, obj: ChatRoom):
        """
            Check if the request user is a member of the room.

            Args:
                request: The current request instance.
                _: The view that is handling the request. Unused in this method, hence the underscore.
                obj: The object being accessed by the request, expected to be an instance of a ChatRoom.

            Returns:
                bool: True if the user is a member of the room, False otherwise.
        """
        return obj.is_member(request.user)
