from rest_framework.serializers import ModelSerializer

from .models import Investor


class InvestorSerializer(ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'
