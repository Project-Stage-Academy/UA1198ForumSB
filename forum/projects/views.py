from django.shortcuts import render

from rest_framework import viewsets, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Project
from .serializers import ProjectSerializer, HistoricalProjectSerializer
from .permissions import UpdateOwnProject


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Project instances.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticated, UpdateOwnProject)
    authentication_classes = (JWTAuthentication,)

class ProjectHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for taking historical records from Project instances.
    """
    serializer_class = HistoricalProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Project.history.filter(id=project_id).order_by('-history_date')
    