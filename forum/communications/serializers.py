from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import CustomUser
from investors.models import Investor
from startups.models import Startup
from .mongo_models import Room, NamespaceInfo


class NamespaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NamespaceInfo
        fields = '__all__'


class RoomSerializer(serializers.Serializer):
    participants = serializers.ListField(
        child=serializers.JSONField()
    )

    def validate(self, data):
        participants = data.get("participants")

        if len(participants) != 2:
            raise serializers.ValidationError

        for participant in participants:
            if not NamespaceInfoSerializer(data=participant).is_valid():
                raise serializers.ValidationError
    
        return data
    
    def create(self, validated_data):
        room_name = ''
        participants = validated_data.get("participants")

        for participant in participants:
            room_name += f'{participant.get('namespace')}_{participant.get('namespace_id')}'

        return Room(name=room_name, **validated_data)


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
