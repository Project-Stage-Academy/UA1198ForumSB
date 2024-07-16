from rest_framework import serializers
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
