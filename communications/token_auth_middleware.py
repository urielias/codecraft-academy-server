from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class TokenAuthMiddleware(BaseMiddleware):
    """
        Middleware for Django Channels that implements token authentication for WebSocket connections.

        This middleware intercepts the connection request to the WebSocket, extracts the token from the query string,
        and attempts to authenticate a user based on this token. If the token is valid, the user associated with the token
        is assigned to the connection's scope, allowing the user to be identified in the consumer. If the token is invalid
        or not provided, the connection is assigned an AnonymousUser, indicating that the request is unauthenticated.

        Attributes:
            None - This class does not define custom attributes beyond those provided by its parent classes.
    """
    async def __call__(self, scope, receive, send):
        """
            Asynchronously intercepts the connection request, extracts the token, and authenticates the user.

            Args:
                scope (dict): The connection scope containing metadata about the request.
                receive (async function): An awaitable callable for receiving messages from the client.
                send (async function): An awaitable callable for sending messages to the client.

            Returns:
                The result of the next middleware in the stack or the consumer if this is the final middleware.
        """
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token')

        # If a token is provided, attempt to authenticate the user.
        if token:
            try:
                user = await self.get_user_from_token(token[0])
                scope['user'] = user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        # Proceed with the connection process.
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """
            Retrieves the user associated with a given authentication token.

            Args:
                token_key (str): The key of the authentication token.

            Returns:
                User: The user instance associated with the given token.
        """
        return Token.objects.get(key=token_key).user
