import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat_group", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        recipient = data.get("recipient", "")

        # Broadcast message to all WebSocket clients
        await self.channel_layer.group_send(
            "chat_group",
            {"type": "chat.message", "message": message, "recipient": recipient},
        )

    async def chat_message(self, event):
        """Send message to WebSocket clients"""
        await self.send(text_data=json.dumps({"message": event["message"]}))
