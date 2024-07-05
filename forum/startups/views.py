from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize
from .serializers import StartupSizeSerializer


class StartupSizeViewSet(GenericViewSet, ListModelMixin):
    queryset = StartupSize.objects.all()

    @swagger_auto_schema(
            responses={
                '200': StartupSizeSerializer
            }
    )
    def list(self, request, *args, **kwargs):
        return Response(
            StartupSizeSerializer(
                self.get_queryset(),
                many=True
            ).data
        )
