from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.validators import CustomUserValidator


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

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


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        request = self.context.get('request')

        if email and password:
            user = authenticate(request=request, email=email, password=password)
            if not user:
                raise AuthenticationFailed("Unable to log in with provided credentials. Please try again)")
        else:
            raise AuthenticationFailed("Email and password  are required")

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data
