from abc import ABC, abstractmethod
from typing import Any

from bson.errors import InvalidId
from bson.objectid import ObjectId
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser

from forum.logging import logger

from .channelsmiddleware import get_user
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
        except Exception as exc:
            logger.error(exc)

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


class NotificationConsumer(BaseCommunicationConsumer):
    async def _auth_user(self) -> CustomUser:
        try:
            access_token = self.scope['url_route']['kwargs']['access_token']
            jwt_payload: dict = AccessToken(access_token).payload

            return await get_user(jwt_payload["user_id"])
        except TokenError:
            raise InvalidToken()
        except Exception:
            # TODO: call logging function
            raise AuthenticationFailed()

    async def connect(self):
        user: CustomUser = None
        if self.scope.get("user"):
            user = self.scope["user"]
        else:
            user = await self._auth_user()

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

    async def _verify_and_send(self, event: dict):
        auto_serializer = AutoSerializer(event, self.room_group_name)
        validated_data = await auto_serializer.apply_for_server_message()
        await self.send_json(validated_data)

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
        except Exception as exc:
            logger.error(exc)

            client_error_builder.build("Something gone wrong, please verify if notification_id is correct")
            await client_error_builder.send(self.room_group_name)
            return

        notification = Notification.objects(pk=notification_id)
        notification_obj = notification.first()
        notification.update(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": self.user_id}
                }
            }
        )

        if not notification_obj.reload().receivers:
            notification_obj.delete()

    async def notify_user(self, event: dict):
        await self._verify_and_send(event)

    async def chat_notification(self, event: dict):
        await self._verify_and_send(event)
