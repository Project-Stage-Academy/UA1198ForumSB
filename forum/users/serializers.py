from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.serializers import ModelSerializer
from .models import CustomUser


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    reset_token = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError(
                {
                    "detail": "Password fields didn't match."
                }
            )

        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError(
                {"detail": e.messages}
            )

        return data


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ['password']
