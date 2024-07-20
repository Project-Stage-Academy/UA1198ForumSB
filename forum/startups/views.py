from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer

from users.permissions import *
from rest_framework.permissions import IsAuthenticated
from .helpers import select_startups_by_search_string, filter_startups, get_details_about_startup


STARTUP_BASE_PERMISSIONS = [
    IsAuthenticated,
    ThisUserPermission,
    IsStartupNamespaceSelected
]


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


class UserStartupsView(APIView):
    permission_classes = STARTUP_BASE_PERMISSIONS

    @swagger_auto_schema(
        operation_description="Retrieve a list of startups",
        operation_summary="List Startups",
        responses={
            '200': StartupSerializer(many=True)
        }
    )
    def get(self, request, user_id):
        startups = Startup.objects.filter(user_id=user_id, is_deleted=False)
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create new startup",
        operation_summary="Create Startup",
        responses={
            '201': StartupSerializer(),
            '400': 'Bad Request'
        }
    )
    def post(self, request, user_id):
        serializer = StartupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStartupView(APIView):
    permission_classes = STARTUP_BASE_PERMISSIONS+[
        ThisStartup
    ]

    @swagger_auto_schema(
        operation_description="Get startup information",
        operation_summary="Get Startup",
        responses={
            '200': StartupSerializer(),
            '404': 'NotFound'
        }
    )
    def get(self, request, user_id, startup_id):
        startup = get_object_or_404(
            Startup.objects.select_related('size').prefetch_related('project'),
            startup_id=startup_id,
            is_deleted=False,
        )
        serializer = StartupSerializer(startup)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update startup information",
        operation_summary="Update Startup",
        responses={
            '200': StartupSerializer(),
            '400': 'Bad Request',
            '404': 'NotFound'
        }
    )
    def patch(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, startup_id=startup_id, is_deleted=False)
        serializer = StartupSerializer(startup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mark startup as deleted",
        operation_summary="Delete Startup",
        responses={
            '204': None,
            '404': 'NotFound'
        }
    )
    def delete(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, startup_id=startup_id, is_deleted=False)
        startup.is_deleted = True
        startup.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

      
class StartupViewSet(ViewSet):
    #TODO only investors can view whole list of startups
    #TODO add appropriate permission
    @swagger_auto_schema(
        operation_description="Retrieve a list of startups based on search criteria",
        operation_summary="List Startups",
        responses={200: StartupSerializer(many=True)}
    )
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
    
    @swagger_auto_schema(
        operation_description="Retrieve detailed information about a specific startup",
        operation_summary="Retrieve Startup",
        responses={200: StartupSerializer}
    )
    def retrieve(self, request, pk):
        startups = Startup.objects.all()
        startup = get_object_or_404(startups, startup_id=pk)
        response_data = get_details_about_startup(startup)
        return Response(response_data, status=200)
