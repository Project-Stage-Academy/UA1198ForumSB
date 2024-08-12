from abc import ABC, abstractmethod
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from investors.models import Investor
from projects.models import Project, ProjectSubscription
from rest_framework.serializers import Serializer
from startups.models import Startup
from users.models import CustomUser

from forum.logging import logger
from forum.settings import EMAIL_HOST_USER
from forum.tasks import send_email_task
from forum.utils import build_email_message

from .exceptions import BaseNotificationException, InvalidDataError, MessageTypeError
from .mongo_models import (
    NamespaceEnum,
    NamespaceInfo,
    Notification,
    NotificationPreferences,
    NotificationTypeEnum,
)
from .serializers import (
    WSChatMessageSerializer,
    WSClientMessageSerializer,
    WSNotificationAckSerializer,
    WSNotificationSerializer,
    WSServerMessageSerializer,
)


class BaseWSMessageBuilder(ABC):
    def __init__(self) -> None:
        self.ws_message: dict[str, Any] = None

    @abstractmethod
    def build(self, *args, **kwargs) -> None:
        ...

    async def send(self, room_name: str):
        channel_layer = get_channel_layer()

        try:
            await channel_layer.group_send(room_name, self.ws_message)
        except ValueError as exc:
            logger.error(exc)


class NotificationBuilder(BaseWSMessageBuilder):
    def build(self, notification: Notification, *args, **kwargs) -> None:
        self.ws_message = {
            "type": "notify_user",
            "notification_id": str(notification.pk),
            "initiator": notification.initiator.to_mongo().to_dict(),
            "message": notification.message,
            "created_at": str(notification.created_at)
        }


class ChatNotificationBuilder(NotificationBuilder):
    def build(self, notification: Notification, *args, **kwargs) -> None:
        super().build(notification)

        if not kwargs.get("message_id"):
            logger.warning(
                "'message_id' was not provided to ChatNotificationBuilder"
            )
            return
        self.ws_message["type"] = "chat_notification"
        self.ws_message["message_id"] = kwargs["message_id"]


class ServerErrorBuilder(BaseWSMessageBuilder):
    def build(self, message: str) -> None:
        self.ws_message = {
            "type": "server_error",
            "message": message,
        }


class ClientErrorBuilder(BaseWSMessageBuilder):
    def build(self, message: str) -> None:
        self.ws_message = {
            "type": "client_error",
            "message": message,
        }


class AutoSerializer:
    MESSAGE_TYPES: dict[str, Serializer] = {
        # for notification about new messages in chat
        "chat_notification": WSChatMessageSerializer,

        # for notifications
        "notify_user": WSNotificationSerializer,

        # for notification acknowledge
        "notification_ack": WSNotificationAckSerializer,

        # server side error (connection will be closed)
        "server_error": WSServerMessageSerializer,

        # client side error (connection will be closed)
        "client_error": WSClientMessageSerializer
    }

    def __init__(self, raw_message: dict, room_name: str) -> None:
        self.raw_message = raw_message
        self.room_name = room_name

    def _has_field_type(self) -> None:
        if not self.raw_message.get("type"):
            raise MessageTypeError()

    def _is_valid_message_type(self) -> bool:
        self._has_field_type()
        return bool(self.MESSAGE_TYPES.get(self.raw_message["type"]))

    async def _get_serializer(self) -> Serializer:
        if not self._is_valid_message_type():
            raise MessageTypeError()

        return self.MESSAGE_TYPES[self.raw_message["type"]]

    async def apply_serializer(self) -> dict:
        """
            Automatically determine which serializer should be used to validate data.
            Return validated data.

        Args:
            raw_message (dict): websocket message
            room_name (str): name of the room to send the message to
            by_client (bool, optional): Side where websocket message built. Defaults to True.
            If the message is built by the client and any error occurs client is responsible for it.

        Returns:
            dict: Validated data
        """

        serializer_class: Serializer = await self._get_serializer()
        serializer: Serializer = serializer_class(data=self.raw_message)
        if not serializer.is_valid():
            raise InvalidDataError()

        return serializer.validated_data

    async def apply_for_client_message(self) -> dict:
        try:
            validated_data = await self.apply_serializer()
            return validated_data
        except BaseNotificationException as exc:
            client_error_builder = ServerErrorBuilder()
            client_error_builder.build(exc.message)
            await client_error_builder.send(self.room_name)

    async def apply_for_server_message(self) -> dict:
        try:
            validated_data = await self.apply_serializer()
            return validated_data
        except BaseNotificationException as exc:
            logger.error(exc)
            server_error_builder = ServerErrorBuilder()
            server_error_builder.build(exc.message)
            await server_error_builder.send(self.room_name)


class NotificationManager(ABC):
    NAMESPACE_NAME: str = None
    NAMESPACE_RECEIVERS_NAME: str = None
    NOTIFICATION_BUILDER_CLASS: NotificationBuilder = NotificationBuilder
    NOTIFICATION_TYPE: str = None

    def __init__(self, namespace_obj: Investor | Startup) -> None:
        self.namespace = namespace_obj

        if not self.NAMESPACE_NAME:
            raise ValueError("Initiator namespace name was not defined")

        if not self.NAMESPACE_RECEIVERS_NAME:
            raise ValueError("Receivers namespace name was not defined")

        if not issubclass(self.NOTIFICATION_BUILDER_CLASS, NotificationBuilder):
            raise ValueError("NOTIFICATION_BUILDER_CLASS should be subclass of NotificationBuilder")

    def _create_initiator_namespace(self) -> NamespaceInfo:
        return NamespaceInfo(
            user_id=self.namespace.user.user_id,
            namespace=self.NAMESPACE_NAME,
            namespace_id=self.get_namespace_id()
        )

    @abstractmethod
    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        ...

    @abstractmethod
    def get_namespace_id(self) -> int:
        ...

    def push_notification(self, message: str, **kwargs):
        initiator_namespace = self._create_initiator_namespace()
        receivers_namespaces = self._create_receivers_namespaces()

        if not receivers_namespaces:
            logger.error(
                f"""
                    Error building notification due to empty receivers list
                    Notification: {message}

                """
            )
            return

        notification = Notification(
            initiator=initiator_namespace,
            receivers=receivers_namespaces,
            message=message
        )
        notification.save()

        notification_builder = self.NOTIFICATION_BUILDER_CLASS()
        notification_builder.build(notification, **kwargs)

        for receiver in notification.receivers:
            async_to_sync(notification_builder.send)(f"notifications_{receiver.user_id}")


class StartupNotificationManager(NotificationManager):
    NAMESPACE_NAME = NamespaceEnum.STARTUP
    NAMESPACE_RECEIVERS_NAME = NamespaceEnum.INVESTOR

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        project: Project = get_object_or_404(
            Project,
            startup_id=self.namespace.startup_id
        )
        for i in ProjectSubscription.objects.filter(project=project):
            user_id = i.investor.user.user_id
            user: CustomUser = get_object_or_404(CustomUser, user_id=user_id)

            if NotificationPreferences.has_preferences(user_id, self.NOTIFICATION_TYPE):
                if NotificationPreferences.is_email_enabled(user_id, self.NOTIFICATION_TYPE):
                    email_context = {
                        'first_name': user.first_name,
                        'notification_type': self.NOTIFICATION_TYPE.value
                    }
                    email_body = build_email_message("email/email_notification.txt",
                                                     email_context)
                    send_email_task.delay(
                        subject="Email Notification",
                        body=email_body,
                        sender=EMAIL_HOST_USER,
                        receivers=user.email
                    )

                receivers.append(
                    NamespaceInfo(
                        user_id=i.investor.user.user_id,
                        namespace=self.NAMESPACE_RECEIVERS_NAME,
                        namespace_id=i.investor.investor_id
                    )
                )

        return receivers

    def get_namespace_id(self) -> int:
        return self.namespace.startup_id


class ProfileUpdateNotificationManager(StartupNotificationManager):
    NOTIFICATION_TYPE = NotificationTypeEnum.PROFILE_UPDATE


class OtherNotificationManager(StartupNotificationManager):  #template
    NOTIFICATION_TYPE = NotificationTypeEnum.NEW_MESSAGE


class InvestorNotificationManager(NotificationManager):
    NAMESPACE_NAME = NamespaceEnum.INVESTOR
    NAMESPACE_RECEIVERS_NAME = NamespaceEnum.STARTUP

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        for i in ProjectSubscription.objects.filter(investor=self.namespace):
            user_id = i.project.startup.user.user_id
            user: CustomUser = get_object_or_404(CustomUser, user_id=user_id)

            if NotificationPreferences.has_preferences(user_id, self.NOTIFICATION_TYPE):
                if NotificationPreferences.is_email_enabled(user_id, self.NOTIFICATION_TYPE):
                    email_context = {
                        'first_name': user.first_name,
                        'notification_type': self.NOTIFICATION_TYPE.value
                    }
                    email_body = build_email_message("email/email_notification.txt",
                                                     email_context)
                    send_email_task.delay(
                        subject="Email Notification",
                        body=email_body,
                        sender=EMAIL_HOST_USER,
                        receivers=user.email
                    )

                receivers.append(
                    NamespaceInfo(
                        user_id=i.project.startup.user.user_id,
                        namespace=self.NAMESPACE_RECEIVERS_NAME,
                        namespace_id=i.project.startup.startup_id
                    )
                )

        return receivers

    def get_namespace_id(self) -> int:
        return self.namespace.investor_id


class ChatNotificationManager(NotificationManager):
    NOTIFICATION_BUILDER_CLASS = ChatNotificationBuilder

    def __init__(self, namespace_obj: Investor | Startup, room) -> None:
        super().__init__(namespace_obj)
        self.room = room

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        # TODO: check if receiver allows notification
        for participant in self.room.participants:
            if (
                participant['namespace_id'] != self.get_namespace_id()
                or participant['namespace'].value != self.NAMESPACE_NAME.value
            ):
                receivers.append(participant)

        return receivers


class InvestorChatNotificationManager(ChatNotificationManager, InvestorNotificationManager):
    pass


class StartupChatNotificationManager(ChatNotificationManager, StartupNotificationManager):
    pass
