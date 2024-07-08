from rest_framework import serializers
from .model import Project, ProjectStatus


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """
    class Meta:
        model = Project
        fields = '__all__'
    
    def validate_budget(self, value):
        if value < 0:
            raise serializers.ValidationError("Budget can not be negative")
        return value