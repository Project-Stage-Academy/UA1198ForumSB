from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from investors.models import Investor
from startups.models import Startup
from .models import CustomUser


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ['password']
        
        
class NamespaceSerializer(serializers.Serializer):
    name_space_id = serializers.IntegerField(required=True)
    name_space_name = serializers.CharField(required=True)
    
    def validate(self, data):
        namespace_id: int = data.get('name_space_id')
        namespace_name: str = data.get('name_space_name')
        user: CustomUser = self.context['user']

        if namespace_name == 'investor':
            get_object_or_404(Investor, user=user, investor_id=namespace_id)
        elif namespace_name == 'startup':
            get_object_or_404(Startup, user=user, startup_id=namespace_id)
        else:
            raise serializers.ValidationError("Invalid namespace.")

        return data