from django.shortcuts import get_object_or_404
from rest_framework import serializers

from investors.models import Investor
from startups.models import Startup
from .mongo_models import Room


class NamespaceInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    namespace = serializers.ChoiceField(choices=[
        ("startup","startup"),
        ("investor","investor")
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
            
            user_id = participant.get("user_id")
            namespace = participant.get("namespace")
            namespace_id = participant.get("namespace_id")
            
            if namespace == "startup":
                namespace_obj = Startup.objects.filter(
                    user__user_id=user_id,
                    startup_id=namespace_id
                ).first()
            
            elif namespace == "investor":
                namespace_obj = Investor.objects.filter(
                    user__user_id=user_id,
                    investor_id=namespace_id
                ).first()
            
            if not namespace_obj:
                raise serializers.ValidationError("Incorrect participants data.")

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
