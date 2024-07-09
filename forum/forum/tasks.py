from django.core.mail import send_mail
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
