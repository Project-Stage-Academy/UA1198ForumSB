from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response

class Util:
    @staticmethod
    def send_email(domain, verification_link, message_data, user_data):
        email = EmailMessage(
            subject=message_data['subject'],
            body= render_to_string(
                "email/email_confirmation_request.txt",
                context={
                    "first_name": user_data['first_name'],
                    "confirmation_email_link": domain + verification_link
                }
            ),
            from_email=message_data['from_email'],
            to=[message_data['to_email']]
        )
        try:
            email.send()
        except Exception:
            return Response(f'An error occurred during sending email', status=status.HTTP_400_BAD_REQUEST)
            
