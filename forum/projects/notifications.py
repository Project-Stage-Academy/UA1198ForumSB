from typing import Literal, TypeAlias
from django.core.exceptions import ValidationError
from forum.tasks import send_email_task
from forum.utils import build_email_message
from startups.models import Startup
from investors.models import Investor
from .models import ProjectSubscription
from forum.logging import logger
from forum.settings import EMAIL_HOST


ActionTypes: TypeAlias = Literal['create', 'update', 'delete']


def validate_project(project):
    reqired_attributes = ['title', 'startup', 'status']

    for attr in reqired_attributes:
        if not hasattr(project, attr):
            raise ValidationError(f"Project must have an attribute '{attr}'")
            
def notify_investors_via_email(project, changes):
    """
    Function notify all subscripted investors about project changes
    """
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
    email_body = build_email_message("email/project_update_notifications_for_investors.txt", email_context)
    recipients = [investor.user_id.email for investor in investors]

    send_email_task.delay(
        subject=f"Update on Project: {project.title}",
        body=email_body,
        sender=EMAIL_HOST,
        receivers=recipients,
    )

def send_notification(project, action: ActionTypes) -> bool | None:
    """
    Function send notification for user profile about project status/changes
    """
    print(f"send_notification called with project: {project} and action: {action}")
    if action not in {'create', 'update', 'delete'}:
        logger.error(f"Invalid action: {action}")
        return

    try:
        validate_project(project)
    except ValidationError as e:
        logger.error(f"Invalid project data: {e}")
        return
    print("Validation passed")

    subject = f"Project {action.capitalize()}"
    message_context = {
        "project_name": project.title,
        "action": action,
        "startup_name": project.startup.name
    }
    try:
        print("Building email message")
        message = build_email_message(
            "email/project_notifications_for_startup.txt",
            message_context
        )
        print("Email message built successfully")
    except Exception as ex:
        logger.error(f"Failed to build email message: {ex}")
        return    
    
    try:
        print("Sending email task")
        send_email_task.delay(
            subject=subject,
            body=message,
            sender=EMAIL_HOST,
            receivers=[project.startup.user.email],  
        )
        print("Email task sent successfully")
    except Exception as ex:
        logger.error(f"Failed to send email: {ex}")
