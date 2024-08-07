from rest_framework_mongoengine.serializers import DocumentSerializer
from .mongo_models import NotificationPreferences, NotificationTypes
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
    created_at = serializers.CharField(required=True)


class WSNotificationAckSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    notification_id = serializers.CharField(required=True)


class NotificationPreferencesSerializer(DocumentSerializer):
    class Meta:
        model = NotificationPreferences
        fields = '__all__'

    def validate_notification_types(self, value):
        if not value:
            raise serializers.ValidationError("At least one notification type must be specified.")
        return value

    def validate(self, data):

        ws_enabled = data.get('ws_enabled')
        email_enabled = data.get('email_enabled')

        if not (ws_enabled or email_enabled):
            raise serializers.ValidationError("At least one notification method (websocket or email) must be enabled.")

        return data