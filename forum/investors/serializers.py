from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from .models import Investor, InvestorStartup
from startups.models import Startup


class InvestorSerializer(ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'


class InvestorSaveStartupSerializer(Serializer):
    investor = serializers.IntegerField(required=True)
    startup = serializers.IntegerField(required=True)

    def validate(self, data):
        investor_id = data.get(investor)
        startup_id = data.get(startup)

        investor = get_object_or_404(Investor, investor_id=investor_id)
        startup = get_object_or_404(Startup, startup_id=startup_id)

        investor_startup_exists = InvestorStartup.objects.filter(
            investor=investor, startup=startup).first()
        
        if investor_startup_exists:
            raise serializers.ValidationError("You have already saved this startup.")
        
        return data
    
    def create(self, validated_data):
        return InvestorStartup.objects.create(validated_data)
