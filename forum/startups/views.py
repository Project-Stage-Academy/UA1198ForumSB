from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer

from .helpers import select_startups_by_search_string, filter_startups, get_details_about_startup


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


class StartupViewSet(ViewSet):
    def list(self, request):
        search_string = request.query_params.get('search')
        if search_string:
            startups = select_startups_by_search_string(search_string)
        elif request.query_params:
            startups = filter_startups(request.query_params)
        else:
            startups = Startup.objects.all()
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=200)
    
    def retrieve(self, request, pk):
        startups = Startup.objects.all()
        startup = get_object_or_404(startups, startup_id=pk)
        response_data = get_details_about_startup(startup)
        return Response(response_data, status=200)

