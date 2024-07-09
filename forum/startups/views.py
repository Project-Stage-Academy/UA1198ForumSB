from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer

from projects.models import Project
from projects.serializers import ProjectSerializer


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
        try:
            startup = Startup.objects.get(startup_id=pk)
        except Startup.DoesNotExist:
            return Response(status=404)
        startup_serializer = StartupSerializer(startup)
        project = Project.objects.filter(startup=startup).first()
        if project:
            project_serializer = ProjectSerializer(project)
            response_detail = {
                **startup_serializer.data,
                "project": project_serializer.data
            }
            return Response(response_detail, status=200)
        return Response(startup_serializer.data, status=200)