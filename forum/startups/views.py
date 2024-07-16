from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer

from users.permissions import *
from rest_framework.permissions import IsAuthenticated


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
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected
    ]

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
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected,
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
