from datetime import timedelta
from os import environ

from django.core.mail import send_mail
from django.db.models.functions import Now
from celery import shared_task


@shared_task(bind=True)
def send_email_task(
    self,  # this name get from docs
    subject: str,
    body: str,
    sender: str,
    receivers: list[str]
) -> int:
    return send_mail(
        subject,
        body,
        sender,
        receivers
    )


@shared_task(bind=True)
def password_reset_ttl_task(self):
    # we should import model on demand cause we could get an error if we imported it globally
    from users.models import PasswordResetModel

    PasswordResetModel.objects.filter(
        created_at__lte=Now() - timedelta(
            minutes=int(environ.get('FORUM_PASSWORD_RESET_TTL', 10))
        )
    ).delete()
