from channels.generic.websocket import AsyncJsonWebsocketConsumer
from users.models import CustomUser

from .utils import apply_serializer


class BaseConsumer(AsyncJsonWebsocketConsumer):
    async def server_error(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name)
        await self.send_json(validated_data, close=True)

    async def client_error(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name)
        await self.send_json(validated_data, close=True)

    async def disconnect(self, code: int):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )


class ChatConsumer(BaseConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"].get("room_name")
        if self.room_name is None:
            await self.close(
                reason="Query parameter 'room_name' was not provided"
            )

        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def receive_json(self, content: dict, **kwargs):
        message = content["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name)
        await self.send_json(validated_data)


class NotificationConsumer(BaseConsumer):
    async def connect(self):
        user: CustomUser = self.scope["user"]

        self.room_group_name = f"notifications_{user.user_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def notify_user(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name)
        await self.send_json(validated_data)
