import logging
import smtplib
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

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
            return True
        except smtplib.SMTPException as e:
            logging.error(f'SMTP error occurred: {e}')
        except Exception as e:
            logging.error(f"An error occurred during sending email to {user_data['first_name']}: {str(e)}")
        return False
