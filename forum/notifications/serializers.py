from rest_framework import serializers

class NamespaceInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    namespace = serializers.CharField(max_length=255)
    namespace_id = serializers.IntegerField()

class NotificationSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    initiator = NamespaceInfoSerializer()
    message = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        if obj.initiator.namespace == 'startup':
            return f'/users/{obj.initiator.user_id}/startups/{obj.initiator.namespace_id}/'
        elif obj.initiator.namespace == 'investor':
            return f'/users/{obj.initiator.user_id}/investors/{obj.initiator.namespace_id}/'
        return None