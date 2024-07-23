from rest_framework import viewsets, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from .models import Project, Industry
from .serializers import ProjectSerializer, HistoricalProjectSerializer, IndustrySerializer
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
