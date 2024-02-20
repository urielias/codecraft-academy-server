import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MyChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept

    async def disconnect(self, code):
        pass

    async def receive(self, data):
        json_data = json.loads(data)
        message = json_data["message"]

        await self.send(text_data=json.dumps({
            "message": message
        }))
