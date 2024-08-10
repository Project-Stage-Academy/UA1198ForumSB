from django.urls import path

from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path(
        "ws/notifications/<access_token>",
        NotificationConsumer.as_asgi(), name="notifications"
    ),
]
