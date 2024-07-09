from os import environ

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from users.models import CustomUser
from .models import PasswordResetModel
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer
)
from .throttling import PasswordResetThrottle


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []
    throttle_classes = [PasswordResetThrottle]

    def post(self, request: Request):
        serializer_data = self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)

        clear_data = serializer_data.validated_data

        user: CustomUser = get_object_or_404(CustomUser, email=clear_data['email'])

        token_generator = PasswordResetTokenGenerator()
        reset_token = token_generator.make_token(user)

        PasswordResetModel.objects.create(
            email=clear_data['email'],
            reset_token=reset_token
        )

        # NOTE: it would be better to use Celery for such tasks
        send_mail(
            "Password Reset Request",
            render_to_string(
                "email/password_reset_request.txt",
                context={
                    "first_name": user.first_name,
                    "reset_link": environ.get('FORUM_PASSWORD_RESET_LINK') + reset_token
                }
            ),
            "from@example.com",
            [user.email],
        )

        return Response(
            {
                "detail": "The email with password reset link is sent to your email"
            }
        )


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = []
    throttle_classes = [PasswordResetThrottle]

    def post(self, request: Request, reset_token: str = None):
        serializer_data = self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)

        clear_data = serializer_data.validated_data

        reset_password_object = PasswordResetModel.objects.filter(
            reset_token=clear_data['reset_token']
        ).first()
        if not reset_password_object:
            raise NotFound(
                {
                    "detail": "Invalid reset token provided"
                }
            )

        user: CustomUser = get_object_or_404(
            CustomUser,
            email=reset_password_object.email
        )
        user.password = clear_data['password']
        user.save()

        reset_password_object.delete()

        return Response(
            {
                "detail": "Password successfully updated"
            }
        )
