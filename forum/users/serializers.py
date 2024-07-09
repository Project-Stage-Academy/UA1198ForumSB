from rest_framework import serializers


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    reset_token = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=255, required=True)
