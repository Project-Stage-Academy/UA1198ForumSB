from bson.errors import InvalidId
from bson.objectid import ObjectId
from rest_framework import serializers

from .helpers import is_namespace_info_correct
from .mongo_models import NamespaceEnum, Room
from .validators import escape_xss


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
            serializer = NamespaceInfoSerializer(data=participant)
            if not serializer.is_valid():
                raise serializers.ValidationError(f"Invalid participant: {serializer.errors}")
            
            is_namespace_info_correct(participant)
        
        namespaces = [p.get("namespace") for p in participants]

        if ("startup" not in namespaces) or ("investor" not in namespaces):
            raise serializers.ValidationError("Room can be created only for investor and startup.")

        return data


class ChatMessageSerializer(serializers.Serializer):
    room = serializers.CharField(required=True)
    author = serializers.JSONField(required=True)
    content = serializers.CharField(required=True)
    
    def validate_content(self, value):
        return escape_xss(value)

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

        serializer = NamespaceInfoSerializer(data=author)
        if not serializer.is_valid():
            raise serializers.ValidationError(f"Invalid author: {serializer.errors}")

        is_namespace_info_correct(author)
        
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
