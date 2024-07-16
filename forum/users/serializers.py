from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from users.models import CustomUser
from users.validators import CustomUserValidator


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)


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
        fields = ('user_id', 'first_name', 'last_name', 'email', 'password', 'password2', 'user_phone', 'description',)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_phone=validated_data.get('user_phone'),
            description=validated_data.get('description')
        )
        return user

    def validate(self, data):
        # Validate that the two password fields match
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Passwords must match.")

        CustomUserValidator.validate_password(data.get('password'))
        if data.get('user_phone') is not None:
            CustomUserValidator.validate_user_phone(data.get('user_phone'))

        return data
