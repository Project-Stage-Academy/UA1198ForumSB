from rest_framework.serializers import ModelSerializer

from .models import Project, ProjectSubscription, Industry


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = ProjectSubscription
        fields = '__all__'


class IndustrySerializer(ModelSerializer):
    class Meta:
        ModelSerializer = Industry
        fields = '__all__'
