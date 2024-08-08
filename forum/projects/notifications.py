from typing import Literal, TypeAlias
from django.core.exceptions import ValidationError
from forum.tasks import send_email_task
from forum.utils import build_email_message
from startups.models import Startup
from investors.models import Investor
from .models import ProjectSubscription
from forum.logging import logger
from forum.settings import EMAIL_HOST
from projects.utils import check_instance


ActionTypes: TypeAlias = Literal['create', 'update', 'delete']


def validate_project(project) -> None:
    """Check if a project has the required attributes.

    Args:
        project (Project): The project instance to validate.

    Raises:
        ValidationError: If any of the required attributes ('title', 'startup', 'status') are missing.
    """
    reqired_attributes = ['title', 'startup', 'status']

    for attr in reqired_attributes:
        if not hasattr(project, attr):
            raise ValidationError(f"Project must have an attribute '{attr}'")
            
def notify_investors_via_email(project, changes) -> None:
    """Notify all subscribed investors about project changes via email.

    Args: 
        project (Project): The project instance for which the notification is being sent.
        changes (dict): A dictionary containing the changes made to the project.

    Raises:
        ValidationError: If the project instance is invalid.
    """
    check_instance(project)
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
    """Send a notification to the user profile about project status or changes.

    Args:
        project (Project): The project instance for which the notification is being sent.
        action (ActionTypes): The action performed on the project. Must be one of 'create', 'update', or 'delete'.

    Returns:
        bool | None: Returns `None` if the validation or email sending fails, otherwise `True`.
    """
    check_instance(project)
    if action not in {'create', 'update', 'delete'}:
        logger.error(f"Invalid action: {action}")
        return

    try:
        validate_project(project)
    except ValidationError as e:
        return

    subject = f"Project {action.capitalize()}"
    message_context = {
        "project_name": project.title,
        "action": action,
        "startup_name": project.startup.name
    }
    try:
        message = build_email_message(
            "email/project_notifications_for_startup.txt",
            message_context
        )
    except Exception as ex:
        logger.error(f"Failed to build email message: {ex}")
        return    
    
    try:
        send_email_task.delay(
            subject=subject,
            body=message,
            sender=EMAIL_HOST,
            receivers=[project.startup.user.email],  
        )
    except Exception as ex:
        logger.error(f"Failed to send email: {ex}")
