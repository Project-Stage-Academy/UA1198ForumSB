from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
