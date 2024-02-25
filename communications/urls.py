from django.urls import path

from .views import ChatHistory

# HTTP URL patterns for the communications app.
urlpatterns = [
    # URL pattern for accessing the chat history of a specific chat room.
    # This route expects a UUID as the `room_id` parameter, which identifies the chat room
    # whose message history is to be retrieved. The `ChatHistory` view handles the request.
    path('chat/<uuid:room_id>/', ChatHistory.as_view(), name='chat_history'),
]
