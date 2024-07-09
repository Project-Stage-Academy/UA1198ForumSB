from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response

class Util:
    @staticmethod
    def send_email(domain, verification_link, message_data, user_data):
        absolute_url = domain + verification_link
        email = EmailMessage(
            subject=message_data['subject'],
            body='Hello ' + user_data['first_name'] + message_data['body'] + absolute_url,
            from_email=message_data['from_email'],
            to=[message_data['to_email']]
        )
        try:
            email.send()
        except Exception:
            return Response(f'An error occurred during sending email', status=status.HTTP_400_BAD_REQUEST)
            
