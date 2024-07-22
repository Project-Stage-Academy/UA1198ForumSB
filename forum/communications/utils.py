from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.serializers import Serializer
from users.models import CustomUser

from .serializers import (
    ChatMessageSerializer,
    WSClientMessageSerializer,
    WSNotificationSerializer,
    WSServerMessageSerializer,
)

MESSAGE_TYPES: dict[str, Serializer] = {
    "chat_message": ChatMessageSerializer,         # used in chat implementation
    "notify_user": WSServerMessageSerializer,      # for notifications
    "notification_ack": WSNotificationSerializer,  # for notification acknowledge
    "server_error": WSServerMessageSerializer,     # server side error (connection will be closed)
    "client_error": WSClientMessageSerializer      # client side error (connection will be closed)
}


def send_raw_ws_message(receiver_id: int, raw_message: dict) -> None:
    channel_layer = get_channel_layer()

    room_name = f"notifications_{receiver_id}"

    async_to_sync(channel_layer.group_send)(room_name, raw_message)


def _is_valid_message_type(message_type: str) -> bool:
    return bool(MESSAGE_TYPES.get(message_type))


def _get_serializer(
    message_type: str,
    room_name: str,
    *,
    by_client: bool = True
) -> Serializer:
    if not _is_valid_message_type(message_type):
        if by_client:
            send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "Invalid field 'type' provided"
                }
            )
            return
        else:
            # TODO: call logging function
            send_raw_ws_message(
                room_name,
                {
                    "type": "server_error",
                    "message": "Something gone wrong, please check if data valid"
                }
            )
            return

    return MESSAGE_TYPES[message_type]


def apply_serializer(
    raw_message: dict,
    room_name: str,
    *,
    by_client: bool = True
) -> dict:
    if not raw_message.get("type"):
        if by_client:
            send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "'type' field was not provided"
                }
            )
            return
        else:
            # TODO: call logging function
            send_raw_ws_message(
                room_name,
                {
                    "type": "server_error",
                    "message": "Something gone wrong, please check if data valid"
                }
            )
            return

    serializer: Serializer = _get_serializer(
        raw_message["type"],
        room_name
    )(data=raw_message)
    if not serializer.is_valid():
        if by_client:
            send_raw_ws_message(
                room_name,
                {
                    "type": "client_error",
                    "message": "Invalid data provided"
                }
            )
            return
        else:
            # TODO: call logging function
            send_raw_ws_message(
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
