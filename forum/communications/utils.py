import asyncio
from typing import Any, Awaitable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.serializers import Serializer

from .serializers import (
    ChatMessageSerializer,
    WSClientMessageSerializer,
    WSNotificationSerializer,
    WSServerMessageSerializer,
)

MESSAGE_TYPES: dict[str, Serializer] = {
    "chat_message": ChatMessageSerializer,         # used in chat implementation
    # TODO: in 23-2 change it to WSNotificationSerializer
    "notify_user": WSServerMessageSerializer,      # for notifications
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


# TODO: this function should be renamed
def send_message(room_name: str, message: str):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        room_name,
        {"type": "chat_message", "message": message}
    )


def send_notification(receivers: int | list[int], message: str | dict):
    channel_layer = get_channel_layer()

    if isinstance(receivers, int):
        receivers = [receivers]

    for user_id in receivers:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user_id}",
            {"type": "notify_user", "message": message}
        )
