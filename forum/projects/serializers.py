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
    
    def create(self, validated_data):
        """
        Create and return a new Project instance, given the validated data.
        """
        return Project.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """
        Update and return an existing Project instance, given the validated data.
        """
        return super().update(instance, validated_data)
