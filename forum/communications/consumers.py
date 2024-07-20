from abc import ABC, abstractmethod

from bson.errors import InvalidId
from bson.objectid import ObjectId
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from users.models import CustomUser

from communications.mongo_models import Notification


class BaseCommunicationConsumer(ABC, AsyncJsonWebsocketConsumer):
    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def disconnect(self, code):
        ...

    @abstractmethod
    async def receive_json(self, content: dict, **kwargs):
        ...


class ChatConsumer(BaseCommunicationConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, code: int):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive_json(self, content: dict, **kwargs):
        message = content["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event: dict):
        message = event["message"]

        await self.send(text_data=message)


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
            # NOTE: we can notify user about wrong ID
            return

        try:
            notification_id = ObjectId(notification_id)
        except InvalidId:
            # NOTE: we can notify user about wrong ID
            return

        Notification.objects(pk=notification_id).update(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": self.user_id}
                }
            }
        )

    async def notify_user(self, event: dict):
        await self.send_json(event)
