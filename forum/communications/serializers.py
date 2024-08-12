from rest_framework_mongoengine.serializers import DocumentSerializer
from .mongo_models import NotificationPreferences, NotificationTypes, NotificationTypeEnum
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


class NotificationTypesSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=[nt.value for nt in NotificationTypeEnum])
    description = serializers.CharField(max_length=255, required=False)

class NotificationPreferencesSerializer(DocumentSerializer):
    notification_types = NotificationTypesSerializer(many=True)

    class Meta:
        model = NotificationPreferences
        fields = ['notification_types', 'ws_enabled', 'email_enabled']

    def create(self, validated_data):
        user_id = self.context['request'].user.user_id
        notification_types_data = validated_data.pop('notification_types')
        notification_types = [NotificationTypes(**nt) for nt in notification_types_data]
        return NotificationPreferences.objects.create(user_id=user_id, notification_types=notification_types, **validated_data)

    def update(self, instance, validated_data):
        notification_types_data = validated_data.pop('notification_types', None)
        if notification_types_data is not None:
            instance.notification_types = [NotificationTypes(**nt) for nt in notification_types_data]
        instance.ws_enabled = validated_data.get('ws_enabled', instance.ws_enabled)
        instance.email_enabled = validated_data.get('email_enabled', instance.email_enabled)
        instance.save()
        return instance