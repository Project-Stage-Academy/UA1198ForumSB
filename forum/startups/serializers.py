from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ErrorDetail, ValidationError

from .models import StartupSize, Startup
from projects.serializers import SimpleProjectSerializer


class StartupSizeSerializer(ModelSerializer):
    class Meta:
        model = StartupSize
        fields = '__all__'


class StartupSerializer(ModelSerializer):
    size = StartupSizeSerializer(required=False)
    project = SimpleProjectSerializer(required=False)

    def validate_user_id(self, user_id):
        if self.validated_data['user'].user_id == user_id:
            return True
        raise ValidationError({"user": ["User does not match the one from url"]})

    class Meta:
        model = Startup
        fields = '__all__'
