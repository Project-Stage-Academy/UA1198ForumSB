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


class WSBaseNotificationSerializer(BaseWSMessageSerializer):
    notification_id = serializers.CharField(required=True)


class WSNotificationSerializer(WSBaseNotificationSerializer):
    initiator = serializers.DictField(required=True)
    created_at = serializers.DateTimeField(required=True)


class WSNotificationAckSerializer(WSBaseNotificationSerializer):
    ...
