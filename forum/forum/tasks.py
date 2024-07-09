from django.core.mail import send_mail
from celery import shared_task


@shared_task(bind=True, ignore_result=True)
def send_email_task(
    subject: str,
    body: str,
    from_email: str,
    receivers: list[str]
) -> int:
    return send_mail(
        subject,
        body,
        from_email,
        receivers
    )
