from abc import ABC, abstractmethod
from typing import Any

from bson.errors import InvalidId
from bson.objectid import ObjectId
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from users.models import CustomUser

from .mongo_models import Notification
from .utils import AutoSerializer, ClientErrorBuilder


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
        auto_serializer = AutoSerializer(event, self.room_group_name)
        validated_data = await auto_serializer.apply_for_server_message()
        await self.send_json(validated_data, close=True)

    async def client_error(self, event: dict):
        auto_serializer = AutoSerializer(event, self.room_group_name)
        validated_data = await auto_serializer.apply_for_server_message()
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
        auto_serializer = AutoSerializer(event, self.room_group_name)
        validated_data = await auto_serializer.apply_for_server_message()
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
        auto_serializer = AutoSerializer(content, self.room_group_name)
        validated_data = await auto_serializer.apply_for_client_message()

        client_error_builder = ClientErrorBuilder()

        try:
            notification_id = ObjectId(validated_data["notification_id"])
        except InvalidId:
            client_error_builder.build("Invalid notification_id was provided")
            await client_error_builder.send(self.room_group_name)
            return
        except Exception:
            # TODO: call logging function
            client_error_builder.build("Something gone wrong, please verify if notification_id is correct")
            await client_error_builder.send(self.room_group_name)
            return

        Notification.objects(pk=notification_id).update(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": self.user_id}
                }
            }
        )

    async def notify_user(self, event: dict):
        auto_serializer = AutoSerializer(event, self.room_group_name)
        validated_data = await auto_serializer.apply_for_server_message()
        await self.send_json(validated_data)