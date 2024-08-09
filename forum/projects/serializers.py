from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Project, ProjectSubscription, Industry


class ProjectSerializer(ModelSerializer):
    """
    Serializer for Project model
    """
    class Meta:
        model = Project
        fields = '__all__'
    
    def validate_budget(self, value):
        if value < 0:
            raise ValidationError("Budget can not be negative")
        return value

class SimpleProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'last_updated']


class ProjectSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = ProjectSubscription
        fields = '__all__'

    def validate(self, data):
        result = super().validate(data)

        if ProjectSubscription.objects.filter(
                investor_id=result["investor"].investor_id, project_id=result["project"].project_id
        ).exists():
            raise ValidationError("Investor already subscribed to the project.")

        if result["project"].budget - result["project"].total_funding <= 0:
            raise ValidationError("Budget is full.")

        return result

    def validate_part(self, value):
        if value == 0:
            raise ValidationError("Part must be greater than 0.")
        return value


class IndustrySerializer(ModelSerializer):
    class Meta:
        model = Industry
        exclude = ['projects']

class HistoricalProjectSerializer(ModelSerializer):
    """
    Historical records serializer
    """
    class Meta:
        model = Project.history.model
        fields = '__all__'
        