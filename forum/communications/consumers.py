from asgiref.sync import async_to_sync
from bson.errors import InvalidId
from bson.objectid import ObjectId
from channels.generic.websocket import JsonWebsocketConsumer
from users.models import CustomUser

from communications.mongo_models import Notification


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        user: CustomUser = self.scope["user"]

        self.user_id = user.user_id
        self.room_group_name = f"notifications_{user.user_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code: int):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive_json(self, content: dict, **kwargs):
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

    def notify_user(self, event: dict):
        self.send_json(event)
