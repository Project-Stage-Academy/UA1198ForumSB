from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    # TODO: implement this serializer in an appropriate task
    ...


class BaseWSMessageSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class WSServerMessageSerializer(BaseWSMessageSerializer):
    ...


class WSClientMessageSerializer(BaseWSMessageSerializer):
    ...


class WSNotificationSerializer(BaseWSMessageSerializer):
    notification_id = serializers.CharField(required=True)
