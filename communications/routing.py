from django.urls import path

from .consumers import ChatConsumer

# WebSocket URL patterns for the communications app.
websocket_urlpatterns = [
    # Defines a WebSocket URL pattern for chat communication.
    # The pattern includes a dynamic segment, <int:receiver_id>, that captures the receiver's user ID from the URL.
    # This ID is then passed to the ChatConsumer, allowing it to know which user is the intended recipient of the message.
    path("ws/chat/<int:receiver_id>/", ChatConsumer.as_asgi())
]
