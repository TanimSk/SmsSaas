import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from forwarder.models import Message


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        await self.channel_layer.group_add("chat_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard("chat_group", self.channel_name)

    async def receive(self, text_data):
        """Handles incoming WebSocket messages"""
        print(f"Received message: {text_data}")

        if text_data != "OK":
            # here, text_data is the message ID
            message = await self.get_message(text_data)
            print(f"Message fetched: {message}")
            if message:
                await self.update_message_status(message)
                print(f"Message updated: {message}")

                # Broadcast message to all WebSocket clients
                # await self.channel_layer.group_send(
                #     "chat_group",
                #     {
                #         "type": "chat.message",
                #         "message": f"{message.id}|{message.status}",
                #     },
                # )

    async def chat_message(self, event):
        """Sends messages to WebSocket clients"""
        message = event["message"]
        await self.send(text_data=message)

    @database_sync_to_async
    def get_message(self, message_id) -> Message:
        """Fetches a message from the database"""
        try:
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            print(f"Message with ID {message_id} not found.")
            return None

    @database_sync_to_async
    def update_message_status(self, message: Message):
        """Updates the message status in the database"""
        message.status = "SENT"
        message.sent_at = timezone.localtime(timezone.now())
        message.save()