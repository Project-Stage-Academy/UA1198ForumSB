from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import ProjectSubscription, Investor

from forum.tasks import build_email_message, send_email_task
from startups.models import Startup


def notify_investors_via_email(project, changes):
    investors = Investor.objects.filter(
        investor_id__in=ProjectSubscription.objects.filter(
            project_id=project.pk
        ).values_list('investor_id', flat=True)
    )
    email_context = {
        'project_title': project.title,
        'changes': changes,
        'startup_name': Startup.objects.get(pk=project.startup.pk).name
    }
    email_body = build_email_message("email/project_update_notification.txt", email_context)
    recipients = [investor.user_id.email for investor in investors]

    send_email_task.delay(
        subject=f"Update on Project: {project.title}",
        body=email_body,
        sender="from@example.com",
        receivers=recipients,
    )
    