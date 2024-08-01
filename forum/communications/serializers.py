from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import CustomUser
from investors.models import Investor
from startups.models import Startup
from .mongo_models import Room


class RoomSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128, required=True)
    participants_id = serializers.ListField(
        child=serializers.IntegerField(required=True)
    )
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def validate(self, data):
        participants_id = data.get("participants_id")

        for id in participants_id:
            get_object_or_404(CustomUser, user_id=id)
    
        return data


class ChatMessageSerializer(serializers.Serializer):
    room = serializers.CharField(required=True)
    namespace_id = serializers.IntegerField(required=True)
    namespace_name = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    timestamp = serializers.DateTimeField()

    def validate(self, data):
        room_id = str(data.get("room").id)
        namespace_id = data.get("namespace_id")
        namespace_name = data.get("namespace_name")
        
        get_object_or_404(Room, id=room_id)

        if namespace_name == "startup":
            get_object_or_404(Startup, startup_id=namespace_id)
        elif namespace_name == "investor":
            get_object_or_404(Investor, startup_id=namespace_id)
        else:
            raise serializers.ValidationError("Invalid namespace")
        
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


class WSNotificationAckSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    notification_id = serializers.CharField(required=True)
