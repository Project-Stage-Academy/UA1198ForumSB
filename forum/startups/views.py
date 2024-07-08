from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize
from .serializers import StartupSizeSerializer


class StartupSizeViewSet(GenericViewSet, ListModelMixin):
    queryset = StartupSize.objects.all()
    serializer_class = StartupSizeSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of startup sizes",
        operation_summary="List StartupSizes",
        responses={
            '200': StartupSizeSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        """
            Retrieve a list of startup sizes.
        """
        return super().list(request, *args, **kwargs)
