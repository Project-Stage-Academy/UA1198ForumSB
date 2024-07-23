from rest_framework import viewsets, permissions

from .models import Project
from .serializers import ProjectSerializer, HistoricalProjectSerializer
from .permissions import UpdateOwnProject
from .services import notify_investors_via_email

from forum.utils import get_changed_fields


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
    