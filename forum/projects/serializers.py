from rest_framework import serializers
from .models import Project


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

class HistoricalProjectSerializer(serializers.ModelSerializer):
    """
    Historical records serializer
    """
    class Meta:
        model = Project.history.model
        fields = '__all__'
        