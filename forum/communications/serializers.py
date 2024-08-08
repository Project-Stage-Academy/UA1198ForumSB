from bson.errors import InvalidId
from bson.objectid import ObjectId
from rest_framework import serializers

from .helpers import is_namespace_info_correct
from .mongo_models import NamespaceEnum, Room


class NamespaceInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    namespace = serializers.ChoiceField(choices=[
        NamespaceEnum.STARTUP.value,
        NamespaceEnum.INVESTOR.value
    ], required=True)
    namespace_id = serializers.CharField(required=True)


class RoomSerializer(serializers.Serializer):
    participants = serializers.ListField()

    def validate(self, data):
        participants = data.get("participants")

        if len(participants) != 2:
            raise serializers.ValidationError("Only two participants in one room.")

        for participant in participants:
            if not NamespaceInfoSerializer(data=participant).is_valid():
                raise serializers.ValidationError("Invalid participant.")

            namespace_obj = is_namespace_info_correct(participant)

            if not namespace_obj:
                raise serializers.ValidationError("Incorrect participants data.")

        namespaces = [p.get("namespace") for p in participants]

        if ("startup" not in namespaces) or ("investor" not in namespaces):
            raise serializers.ValidationError("Room can be created only for investor and startup.")

        return data


class ChatMessageSerializer(serializers.Serializer):
    room = serializers.CharField(required=True)
    author = serializers.JSONField(required=True)
    content = serializers.CharField(required=True)

    def validate(self, data):
        room_id = data.get("room")
        author = data.get("author")

        try:
            room_id = ObjectId(room_id)
        except InvalidId:
            raise serializers.ValidationError("Invalid room id.")

        room_exists = Room.objects.filter(id=room_id).first()
        if not room_exists:
            raise serializers.ValidationError("Room does not exist.")

        if not NamespaceInfoSerializer(data=author).is_valid():
            raise serializers.ValidationError("Invalid author.")

        author_is_correct = is_namespace_info_correct(author)

        if not author_is_correct:
            raise serializers.ValidationError("Incorrect author data.")

        return data


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


class WSChatMessageSerializer(WSNotificationSerializer):
    message_id = serializers.CharField(required=True)


class WSNotificationAckSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    notification_id = serializers.CharField(required=True)
