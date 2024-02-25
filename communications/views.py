from .models import Message, ChatRoom
from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsAuthenticated

from .permissions import IsMemberOfRoom
from .serializers import MessageSerializer


class ChatHistory(APIView):
    """
        API view for retrieving the message history of a chat room.

        This view enforces authentication and room membership checks before providing access
        to the chat history of a specific room. It utilizes custom permissions to ensure that
        only authenticated members of the specified room can retrieve its message history.

        Attributes:
            permission_classes (list): A list of permission classes that the request must
            satisfy to access this view. Includes checks for user authentication and membership
            in the specified chat room.
    """
    permission_classes = [IsAuthenticated, IsMemberOfRoom]

    def get(self, request, room_id):
        """
            Handles GET requests to retrieve the message history for a specified chat room.

            Args:
                request: The HTTP request instance.
                room_id: The ID of the chat room whose message history is being requested.

            Returns:
                Response: Response object containing the serialized message history
                if the room exists and the request passes the permission checks. If the room
                does not exist, returns a 404 response with an error message.
        """
        try:
            # Attempt to retrieve the specified chat room by ID.
            room = ChatRoom.objects.get(id=room_id)

            # Perform permission checks defined in `permission_classes`.
            self.check_object_permissions(request, obj=room)

            # Retrieve and serialize the messages from the specified room.
            messages = Message.objects.filter(room=room).order_by('timestamp')
            serializer = MessageSerializer(messages, many=True)

            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=404)
