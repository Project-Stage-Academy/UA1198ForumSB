from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer


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


class StartupViewSet(ViewSet):
    def list(self, request):
        startups = Startup.objects.all()
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=200)
    
    def retrieve(self, request, pk):
        startups = Startup.objects.all()
        startup = get_object_or_404(startups, pk)
        serializer = StartupSerializer(startup)
        return Response(serializer.data, status=200)
