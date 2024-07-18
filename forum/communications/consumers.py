from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from users.models import CustomUser


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, code: int):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive_json(self, content: dict, **kwargs):
        message = content["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def chat_message(self, event: dict):
        message = event["message"]

        self.send(text_data=message)


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        user: CustomUser = self.scope["user"]

        self.room_group_name = f"notifications_{user.user_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def notify_user(self, event: dict):
        self.send_json(event)
