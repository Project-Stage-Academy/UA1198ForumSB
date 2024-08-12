from rest_framework import viewsets, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Project, Industry
from .serializers import ProjectSerializer, HistoricalProjectSerializer, IndustrySerializer
from .permissions import UpdateOwnProject
from .notifications import notify_investors_via_email, send_notification
from .utils import get_changed_fields

from users.permissions import (
    ThisUserPermission,
    IsStartupNamespaceSelected,
    ThisStartup)
from startups.models import Startup

from drf_yasg.utils import swagger_auto_schema


class UserStartupProjectView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected,
        ThisStartup,
        UpdateOwnProject
    ]

    def get(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id, is_deleted=False)
        project = get_object_or_404(Project, startup=startup, is_deleted=False)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id, startup_id):
        serializer = ProjectSerializer(data={
            **request.data,
            'user': user_id,
            'startup': startup_id
        })
        if serializer.is_valid():
            project = serializer.save()
            send_notification(project, "create")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            updated_project = serializer.save()
            changes = get_changed_fields(project, updated_project)
            if changes:
                notify_investors_via_email(updated_project, changes)
                send_notification(updated_project, "update")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for taking historical records from Project instances.
    """
    serializer_class = HistoricalProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Project.history.filter(id=project_id).order_by('-history_date')

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
