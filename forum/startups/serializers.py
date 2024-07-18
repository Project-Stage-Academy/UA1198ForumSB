from rest_framework.serializers import ModelSerializer

from .models import StartupSize, Startup


class StartupSizeSerializer(ModelSerializer):
    class Meta:
        model = StartupSize
        fields = '__all__'


class StartupSerializer(ModelSerializer):
    class Meta:
        model = Startup
        fields = '__all__'
