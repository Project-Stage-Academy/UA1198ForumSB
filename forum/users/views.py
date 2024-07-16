from os import environ

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.urls import reverse
import jwt
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from users.models import CustomUser
from forum.tasks import send_email_task
from forum.utils import build_email_message
from .models import PasswordResetModel
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer
)
from .throttling import PasswordResetThrottle
from forum import settings
from users.serializers import UserRegisterSerializer
from users.utils import Util
from users.swagger_auto_schema_settings import (
    userRegisterView_request_body,
    userRegisterView_responses,
    sendEmailConfirmationView_responses
)


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

        send_email_task.delay(
            subject="Password Reset Request",
            body=build_email_message(
                "email/password_reset_request.txt",
                {
                    "first_name": user.first_name,
                    "reset_link": environ.get('FORUM_PASSWORD_RESET_LINK') + reset_token
                }
            ),
            sender="from@example.com",
            receivers=[user.email],
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


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Sending a confirmation email after successful validation of user data",
        operation_summary="User Registration",
        request_body=userRegisterView_request_body,
        responses=userRegisterView_responses,
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            token = RefreshToken()

            for key, value in user_data.items():
                token[key] = str(value)

            message_data = {
                'subject': 'Verify your email',
                'from_email': settings.EMAIL_HOST_USER,
                'to_email': user_data['email']
            }
            domain = get_current_site(request).domain
            verification_link = reverse('users:email-verify', kwargs={'token': str(token)})
            email_sent = Util.send_email(domain, verification_link, message_data, user_data)
            if email_sent:
                return Response("Verification link was sent to your email", status=status.HTTP_200_OK)
            else:
                return Response({"error": "An error occurred during sending email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SendEmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Creating a new user after successful confirmation email",
        operation_summary="Confirmation Email",
        responses=sendEmailConfirmationView_responses,
    )
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])

            if CustomUser.objects.filter(email=payload['email']).exists():
                return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = UserRegisterSerializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return Response({"error": "Verification link expired"}, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
