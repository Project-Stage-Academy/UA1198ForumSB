from abc import ABC, abstractmethod
from typing import Any

from bson.errors import InvalidId
from bson.objectid import ObjectId
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from users.models import CustomUser

from communications.mongo_models import Notification

from .utils import apply_serializer


class BaseCommunicationConsumer(ABC, AsyncJsonWebsocketConsumer):
    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def receive_json(self, content: dict, **kwargs):
        ...

    async def send_json(self, content: Any, close: bool = False):
        try:
            await super().send_json(content, close)
        except Exception:
            # TODO: call logging function
            ...

    async def server_error(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name, by_client=False)
        await self.send_json(validated_data, close=True)

    async def client_error(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name, by_client=False)
        await self.send_json(validated_data, close=True)

    async def disconnect(self, code: int):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )


class ChatConsumer(BaseCommunicationConsumer):
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
        validated_data = await apply_serializer(event, self.room_group_name, by_client=False)
        await self.send_json(validated_data)


class NotificationConsumer(BaseCommunicationConsumer):
    async def connect(self):
        user: CustomUser = self.scope["user"]

        self.user_id = user.user_id
        self.room_group_name = f"notifications_{user.user_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code: int):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive_json(self, content: dict, **kwargs):
        notification_id = content.get("notification_id")
        if not notification_id:
            await self.send_json(
                {"message": "notification_id was not provided"},
                close=True
            )

        try:
            notification_id = ObjectId(notification_id)
        except InvalidId:
            await self.send_json(
                {"message": "Invalid notification_id was provided"},
                close=True
            )
        except Exception:
            # TODO: call logging function
            await self.send_json(
                {"message": "Something gone wrong, please verify if notification_id is correct"},
                close=True
            )

        Notification.objects(pk=notification_id).update(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": self.user_id}
                }
            }
        )

    async def notify_user(self, event: dict):
        validated_data = await apply_serializer(event, self.room_group_name, by_client=False)
        await self.send_json(validated_data)