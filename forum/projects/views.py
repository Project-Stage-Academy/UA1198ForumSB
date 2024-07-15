from django.shortcuts import render

from rest_framework import viewsets, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Project, Investor, ProjectSubscription
from .serializers import ProjectSerializer, HistoricalProjectSerializer
from .permissions import UpdateOwnProject

from startups.models import Startup
from forum.utils import get_changed_fields, build_email_message
from forum.tasks import send_email_task


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Project instances.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticated, UpdateOwnProject)
    authentication_classes = (JWTAuthentication,)

    def perform_update(self, serializer):
        instance = serializer.save()
        old_instance = Project.objects.get(pk=instance.pk)
        changes = get_changed_fields(old_instance, instance)

        if changes:
            investors = Investor.objects.filter(
                investor_id__in=ProjectSubscription.objects.filter(
                    project_id=instance
                ).values_list('investord_id', flat=True)
            )
            email_context = {
                'project_title': instance.title,
                'changes': changes,
                'startap_name': Startup.objects.get(pk=instance.startup).name
            }
            email_body = build_email_message("email/project_update_notification.txt",
                                             email_context)
            recipients = [investor.user_id.email for investor in investors]
            send_email_task.delay(
                subject=f"Update on Project: {instance.title}",
                body=email_body,
                sender="from@example.com",
                receivers=recipients,
            )


class ProjectHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for taking historical records from Project instances.
    """
    serializer_class = HistoricalProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Project.history.filter(id=project_id).order_by('-history_date')
    