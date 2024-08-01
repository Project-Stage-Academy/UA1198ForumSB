from rest_framework import serializers

from communications.mongo_models import NamespaceEnum

from .utils import URLGenerator


class NamespaceInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    namespace = serializers.ChoiceField(choices=[x.name for x in NamespaceEnum])
    namespace_id = serializers.IntegerField()


class NotificationSerializer(serializers.Serializer):
    notification_id = serializers.CharField(source="id", read_only=True)
    initiator = NamespaceInfoSerializer()
    message = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return URLGenerator.generate_url(
            namespace=obj.initiator.namespace,
            user_id=obj.initiator.user_id,
            namespace_id=obj.initiator.namespace_id
        )
