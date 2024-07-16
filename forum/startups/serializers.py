from rest_framework.serializers import ModelSerializer

from .models import StartupSize, Startup
from projects.serializers import SimpleProjectSerializer


class StartupSizeSerializer(ModelSerializer):
    class Meta:
        model = StartupSize
        fields = '__all__'


class StartupSerializer(ModelSerializer):
    size = StartupSizeSerializer(required=False)
    project = SimpleProjectSerializer(required=False)

    class Meta:
        model = Startup
        fields = '__all__'
