import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from investors.models import Investor
from projects.models import Project, ProjectSubscription
from rest_framework.serializers import Serializer
from startups.models import Startup

from .mongo_models import NamespaceInfo, Notification
from .serializers import (
    ChatMessageSerializer,
    WSClientMessageSerializer,
    WSNotificationSerializer,
    WSServerMessageSerializer,
)

MESSAGE_TYPES: dict[str, Serializer] = {
    "chat_message": ChatMessageSerializer,         # used in chat implementation
    "notify_user": WSNotificationSerializer,      # for notifications
    "notification_ack": WSNotificationSerializer,  # for notification acknowledge
    "server_error": WSServerMessageSerializer,     # server side error (connection will be closed)
    "client_error": WSClientMessageSerializer      # client side error (connection will be closed)
}


def run_in_loop(future: Awaitable) -> Any:
    # NOTE: we can use another implementation
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)


async def send_raw_ws_message(room_name: str, raw_message: dict) -> None:
    channel_layer = get_channel_layer()

    try:
        await channel_layer.group_send(room_name, raw_message)
    except ValueError:
        # TODO: call logging function
        # no handler for this message type
        ...


def _is_valid_message_type(message_type: str) -> bool:
    return bool(MESSAGE_TYPES.get(message_type))


async def _get_serializer(
    message_type: str,
    room_name: str,
    *,
    by_client: bool = True
) -> Serializer:
    if not _is_valid_message_type(message_type):
        if by_client:
            await send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "Invalid field 'type' provided"
                }
            )
            return
        else:
            # TODO: call logging function
            await send_raw_ws_message(
                room_name,
                {
                    "type": "server_error",
                    "message": "Something gone wrong, please check if data valid"
                }
            )
            return

    return MESSAGE_TYPES[message_type]


async def apply_serializer(
    raw_message: dict,
    room_name: str,
    *,
    by_client: bool = True
) -> dict:
    """
        Automatically determine which serializer should be used to validate data.
        Return validated data.

    Args:
        raw_message (dict): websocket message
        room_name (str): _description_
        by_client (bool, optional): Side where websocket message built. Defaults to True.
        If the message is built by the client and any error occurs client is responsible for it.

    Returns:
        dict: Validated data
    """

    if not raw_message.get("type"):
        if by_client:
            await send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "'type' field was not provided"
                }
            )
            return
        else:
            # TODO: call logging function
            await send_raw_ws_message(
                room_name,
                {
                    "type": "server_error",
                    "message": "Something gone wrong, please check if data valid"
                }
            )
            return

    serializer_class: Serializer = await _get_serializer(
        raw_message["type"],
        room_name
    )
    serializer: Serializer = serializer_class(data=raw_message)
    if not serializer.is_valid():
        if by_client:
            await send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "Invalid data provided"
                }
            )
            return
        else:
            # TODO: call logging function
            await send_raw_ws_message(
                room_name,
                {
                    "type": "server_error",
                    "message": "Something gone wrong, please check if data valid"
                }
            )
            return

    return serializer.validated_data


def send_notification(notification: Notification):
    channel_layer = get_channel_layer()

    for receiver in notification.receivers:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{receiver.user_id}",
            {
                "type": "notify_user",
                "notification_id": str(notification.pk),
                "message": notification.message
            }
        )


class NotificationManager(ABC):
    NAMESPACE_NAME: str = None
    NAMESPACE_RECEIVERS_NAME: str = None

    def __init__(self, namespace_obj: Investor | Startup) -> None:
        self.namespace = namespace_obj

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

    def push_notification(self, message: str):
        initiator_namespace = self._create_initiator_namespace()
        receivers_namespaces = self._create_receivers_namespaces()

        notification = Notification(
            initiator=initiator_namespace,
            receivers=receivers_namespaces,
            message=message
        )
        notification.save()

        send_notification(notification)


class StartupNotificationManager(NotificationManager):
    NAMESPACE_NAME = "startup"
    NAMESPACE_RECEIVERS_NAME = "investor"

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        project: Project = get_object_or_404(
            Project,
            startup_id=self.namespace.startup_id
        )
        for i in ProjectSubscription.objects.filter(project=project):
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


class InvestorNotificationManager(NotificationManager):
    NAMESPACE_NAME = "investor"
    NAMESPACE_RECEIVERS_NAME = "startup"

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        for i in ProjectSubscription.objects.filter(investor=self.namespace):
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
