from rest_framework import viewsets, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from users.permissions import get_token_payload_from_cookies
from investors.permissions import InvestorPermission
from rest_framework import status

from .models import Project, Industry
from .serializers import (
    ProjectSerializer,
    HistoricalProjectSerializer,
    IndustrySerializer,
    ProjectSubscriptionSerializer
)
from .permissions import UpdateOwnProject
from .services import notify_investors_via_email

from forum.utils import get_changed_fields


from drf_yasg.utils import swagger_auto_schema


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Project instances.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, UpdateOwnProject)

    def perform_update(self, serializer):
        instance = serializer.save()
        old_instance = Project.objects.get(pk=instance.pk)
        changes = get_changed_fields(old_instance, instance)

        if changes:
            notify_investors_via_email(instance, changes)


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


class ProjectSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, InvestorPermission]

    def post(self, request, project_id):
        payload = get_token_payload_from_cookies(request)
        investor_id = payload.get("name_space_id")
        investor_subscribe_project_data = {
            "investor": investor_id,
            "project": project_id,
            "part": request.data.get("part")
        }
        serializer = ProjectSubscriptionSerializer(data=investor_subscribe_project_data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                "The investor has been successfully subscribed to the project.",
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
