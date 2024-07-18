from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema

from .models import Industry
from .serializers import IndustrySerializer


class IndustryViewSet(GenericViewSet, ListModelMixin):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of industries",
        operation_summary="List Industries",
        responses={
            '200': IndustrySerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        """
            Receive a list of industries.
        """
        return super().list(request, *args, **kwargs)
