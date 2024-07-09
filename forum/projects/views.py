from django.shortcuts import render

from rest_framework import viewsets, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Project
from .serializers import ProjectSerializer
from .permissions import UpdateOwnProject


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Project instances.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticated, UpdateOwnProject)
    authentication_classes = (JWTAuthentication,)
